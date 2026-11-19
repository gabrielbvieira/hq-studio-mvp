"""Geração pelo ChatGPT no Chrome, usando o chatgpt-image-cli instalado localmente."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import uuid
from pathlib import Path


# Fotos grandes demoram para subir no ChatGPT antes de o texto ser enviado; acima disto, viram JPEG menor.
MAX_REFERENCE_SIDE = 1536
MAX_REFERENCE_BYTES = 1_500_000


def compact_reference(source: Path, target_dir: Path) -> Path:
    """Copia a referência; se for grande, reduz para no máximo 1536 px em JPEG (bem mais rápido de enviar)."""
    from PIL import Image
    target = target_dir / source.name
    try:
        with Image.open(source) as image:
            large = max(image.size) > MAX_REFERENCE_SIDE or source.stat().st_size > MAX_REFERENCE_BYTES
            if large:
                target = target_dir / (source.stem + '.jpg')
                image = image.convert('RGB')
                image.thumbnail((MAX_REFERENCE_SIDE, MAX_REFERENCE_SIDE))
                image.save(target, 'JPEG', quality=88, optimize=True)
                return target
    except OSError:
        pass   # formato que o Pillow não abre: envia como está
    shutil.copyfile(source, target)
    return target


BRIDGE_URL = 'https://chromewebstore.google.com/detail/playwright-mcp-bridge/mmlmfjhmonkocbjadbfplnigmagldckm'


def chatgpt_web_prompt(prompt: str) -> str:
    lines = [line for line in prompt.splitlines() if not line.startswith('SALVE obrigatoriamente')]
    return ('\n'.join(lines).replace('(na pasta ./referencias/ e, quando anexadas, nesta mesma ordem)',
                                    '(anexadas nesta mesma ordem)')
            + '\n\nGere a imagem agora e entregue a imagem gerada nesta conversa. '
              'As imagens anexadas seguem a ordem da lista de referências acima.')


class ChatGPTWebClient:
    def __init__(self, base: Path):
        self.base = base.resolve()
        self.cli = self.base / 'data' / 'tools' / 'chatgpt-image-cli' / 'dist' / 'cli.js'
        self.home = self.base / 'data' / 'chatgpt_web'
        self.lock = threading.Lock()

    def available(self) -> bool:
        # Instalação local disponível; login e conexão são verificados somente ao gerar.
        return bool(shutil.which('node') and self.cli.is_file())

    def environment(self) -> dict:
        env = os.environ.copy()
        env['CHATGPT_IMAGE_HOME'] = str(self.home / 'cli')
        env['NO_UPDATE_NOTIFIER'] = '1'
        # Tempo de cada passo no navegador (sem o texto do pedido), para achar o que deixa a geração lenta.
        env['CHATGPT_IMAGE_TIMING_LOG'] = str(self.home / 'timing.log')
        # Grupo de abas da extensão com o nome do app (vale a partir da próxima conexão com o Chrome).
        env['PLAYWRIGHT_MCP_TAB_GROUP_TITLE'] = 'HQ Studio'
        env['PLAYWRIGHT_MCP_TAB_GROUP_COLOR'] = 'purple'
        # Trabalha em segundo plano: abas do ChatGPT abrem sem tirar o foco da aba do HQ Studio.
        env['PLAYWRIGHT_MCP_BACKGROUND'] = '1'
        # Opcional: configurado localmente, sem devolver o segredo ao app ou aos logs.
        token_file = self.home / 'bridge-token'
        if token_file.is_file():
            token_file.chmod(0o600)
            env['PLAYWRIGHT_MCP_EXTENSION_TOKEN'] = token_file.read_text(encoding='utf-8').strip()
        return env

    def generate(self, prompt: str, references: list[Path], frame_id: str, refine: bool = False) -> Path:
        with self.lock:
            try:
                return self._generate(prompt, references, frame_id, refine)
            except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError):
                raise RuntimeError('Falha na conexão com o ChatGPT no navegador. Confira a extensão Playwright Bridge '
                                   'e tente novamente. O pedido local foi preservado para retomar sem envio duplicado.') from None

    def _generate(self, prompt: str, references: list[Path], frame_id: str, refine: bool) -> Path:
        self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.home.chmod(0o700)
        frames = self.home / 'frames'
        frames.mkdir(exist_ok=True, mode=0o700)
        state_file = frames / (hashlib.sha256(frame_id.encode()).hexdigest() + '.json')
        state = json.loads(state_file.read_text(encoding='utf-8')) if state_file.exists() else {}
        if not isinstance(state, dict):
            raise ValueError('Invalid local task state')
        thread = state.get('thread_id', '') if refine else ''
        if not isinstance(thread, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,200}', thread):
            thread = ''
        digest = hashlib.sha256(json.dumps([prompt, refine, thread]).encode())
        for reference in references:
            digest.update(reference.name.encode())
            with reference.open('rb') as source:
                while chunk := source.read(1024 * 1024):
                    digest.update(chunk)
        fingerprint = digest.hexdigest()
        task_id = state.get('task_id', '')
        reuse = (state.get('pending') and state.get('fingerprint') == fingerprint
                 and isinstance(task_id, str) and re.fullmatch(r'hq-[a-f0-9]{32}', task_id))
        if not reuse:
            task_id = 'hq-' + uuid.uuid4().hex
        task = self.home / 'requests' / task_id
        task.mkdir(parents=True, exist_ok=True, mode=0o700)
        request_file = task / 'request.json'
        if not reuse:
            refs_dir = task / 'references'
            refs_dir.mkdir(mode=0o700)
            copied = []
            for reference in references:
                target = compact_reference(reference, refs_dir)
                if target.name != reference.name:
                    # O pedido cita as fotos pelo nome; acompanha a troca de .png para .jpg.
                    prompt = prompt.replace(reference.name, target.name)
                copied.append(str(target))
            request = {'task_id': task_id, 'mode': 'continue' if thread else 'new', 'prompt': prompt,
                       'reference_images': copied, 'output_dir': str(task / 'images'), 'timeout_seconds': 600,
                       'force_resubmit': False,
                       'browser': {'connection': 'extension', 'channel': 'chrome', 'session_name': 'hq-studio'}}
            if thread:
                request['thread_id'] = thread
            self._write(request_file, request)
            state.update(task_id=task_id, fingerprint=fingerprint, pending=True)
            self._write(state_file, state)
        # Reusar o mesmo task_id faz o CLI retomar o pedido existente, sem reenviar o prompt.
        proc = subprocess.run([shutil.which('node') or 'node', str(self.cli), 'run', '--input', str(request_file)],
                              cwd=self.home, env=self.environment(), capture_output=True, text=True,
                              timeout=1000, check=False)
        result = json.loads(proc.stdout)
        if not isinstance(result, dict):
            raise ValueError('Invalid CLI response')
        status = result.get('status')
        if proc.returncode or status != 'completed':
            error = result.get('error') or {}
            code = error.get('code') if isinstance(error, dict) else ''
            messages = {
                'login_required': 'Entre na sua conta em chatgpt.com no Chrome e tente novamente.',
                'human_action_required': 'O Chrome precisa da sua intervenção. Instale ou autorize a extensão Playwright Bridge '
                                         'e conclua qualquer verificação na aba do ChatGPT. Depois tente novamente.',
                'content_blocked': 'O ChatGPT não aceitou esse pedido de imagem. Ajuste a descrição antes de gerar novamente.',
                'timed_out': 'O ChatGPT ainda não terminou a imagem. Clique em Gerar novamente com o mesmo pedido para retomar sem reenviar.',
                'download_failed': 'A imagem foi solicitada, mas o download não terminou. Tente novamente com o mesmo pedido para retomar.',
                'ui_changed': 'A ferramenta não reconheceu a interface atual do ChatGPT. Confira a aba no Chrome.',
            }
            if code == 'browser_extension_not_installed':
                raise RuntimeError('Instale a extensão oficial Playwright Bridge no Chrome: ' + BRIDGE_URL
                                   + '. Depois entre em chatgpt.com e tente novamente.')
            if code == 'submission_uncertain':
                raise RuntimeError('O envio não foi confirmado. Confira a conversa no Chrome e repita o mesmo pedido '
                                   'para retomar; o app não reenviará uma mensagem já confirmada.')
            if code in ('upload_not_confirmed', 'upload_failed'):
                raise RuntimeError('O Chrome não confirmou todas as imagens de referência. Confira os anexos na aba '
                                   'do ChatGPT e tente novamente. O pedido não foi enviado sem as referências.')
            raise RuntimeError(messages.get(status, 'Não foi possível concluir a geração pelo ChatGPT. '
                                                   'Confira a conexão com o Chrome e tente novamente.'))
        images = result.get('images') or []
        if not images:
            raise RuntimeError('O ChatGPT encerrou o pedido sem entregar uma imagem.')
        image = Path(images[0]['path']).resolve()
        if not image.is_relative_to((task / 'images').resolve()) or not image.is_file():
            raise RuntimeError('O ChatGPT não entregou um arquivo de imagem válido na pasta do pedido.')
        state['pending'] = False
        # Imagem salva: apaga a conversa no ChatGPT para não acumular chats. O Refinar seguinte começa uma
        # conversa nova, levando a imagem atual do quadro como referência.
        state['thread_id'] = '' if self._delete_conversation(task_id) else (result.get('thread_id') or thread)
        self._write(state_file, state)
        return image

    def _delete_conversation(self, task_id: str) -> bool:
        """Falhar aqui não estraga a geração: a imagem já foi baixada; o chat só fica no histórico."""
        try:
            proc = subprocess.run([shutil.which('node') or 'node', str(self.cli), 'delete', '--task-id', task_id],
                                  cwd=self.home, env=self.environment(), capture_output=True, text=True,
                                  timeout=120, check=False)
            return proc.returncode == 0 and json.loads(proc.stdout).get('status') == 'ok'
        except (OSError, ValueError, AttributeError, subprocess.SubprocessError):
            return False

    @staticmethod
    def _write(path: Path, data: dict):
        temporary = path.with_suffix('.tmp')
        with temporary.open('w', encoding='utf-8') as output:
            temporary.chmod(0o600)
            json.dump(data, output, ensure_ascii=False)
        temporary.replace(path)
