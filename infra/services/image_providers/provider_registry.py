"""Adaptadores de geração; a camada de domínio não conhece estes clientes."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import re
import shutil
import subprocess
import textwrap
import threading
import time
import uuid
from html import escape
from pathlib import Path

from infra.services.image_files import file_type
from infra.services.image_providers.chatgpt_web import ChatGPTWebClient, chatgpt_web_prompt


SUPPORTED_SUFFIXES = ('.png', '.webp', '.jpg', '.jpeg')
EFFORTS = ['low', 'medium', 'high', 'xhigh', 'max']   # 'ultra' do Codex fica de fora: delega tarefas e gasta muito mais


ANTIGRAVITY_HOME = Path(os.environ.get('ANTIGRAVITY_HOME', Path.home() / '.gemini' / 'antigravity-cli'))
AGY_SUFFIX = ('\n\nPara o Antigravity: gere a imagem com a sua ferramenta de geração de imagem. Se não conseguir salvar '
              'quadro.png na pasta de trabalho, não use comandos de terminal para copiar: o app pega a imagem gerada sozinho.')
_agy_cache: dict = {'at': 0.0, 'models': []}


def agy_models() -> list[dict]:
    """Modelos que o `agy models` lista para a conta; guardado por 10 minutos (o comando leva alguns segundos)."""
    if time.monotonic() - _agy_cache['at'] < 600:
        return _agy_cache['models']
    models = []
    try:
        out = subprocess.run(['agy', 'models'], capture_output=True, text=True, timeout=20, check=False,
                             stdin=subprocess.DEVNULL).stdout
        for line in out.splitlines():
            slug, _, name = line.partition('\t')
            if slug.strip() and name.strip():
                models.append({'id': slug.strip(), 'name': name.strip()})
    except (OSError, subprocess.SubprocessError):
        pass
    _agy_cache.update(at=time.monotonic(), models=models)
    return models


def antigravity_image(stdout: str, started: float, home: Path = ANTIGRAVITY_HOME) -> Path | None:
    """A ferramenta de imagem do Antigravity salva na pasta da conversa (ou do subagente), não na de trabalho.
    A saída JSON diz qual é a conversa; pega a imagem mais nova criada durante esta execução."""
    try:
        conversation = json.loads(stdout.strip().splitlines()[-1])['conversation_id']
    except (ValueError, KeyError, IndexError, TypeError):
        return None
    brain = home / 'brain'
    folders = [brain / conversation]
    subagents = brain / conversation / '.system_generated' / 'subagents'
    if subagents.is_dir():
        folders += [brain / item.stem for item in subagents.glob('*.json')]
    images = [path for folder in folders if folder.is_dir() for path in folder.rglob('*')
              if path.suffix.lower() in SUPPORTED_SUFFIXES and path.is_file() and path.stat().st_mtime >= started]
    return max(images, key=lambda path: path.stat().st_mtime, default=None)


GEMINI_WEB_SUFFIX = ('\n\nGere a imagem agora: responda com a imagem gerada, não só com texto. '
                     'As imagens anexadas seguem a ordem da lista de referências acima.')


class GeminiWebError(RuntimeError):
    """Mensagem do app que pode ser exibida sem revelar dados da sessão."""


def gemini_web_prompt(prompt: str) -> str:
    """O chat do Gemini não salva arquivos: tira as instruções de pasta/arquivo e pede a imagem na resposta."""
    lines = [line for line in prompt.splitlines() if not line.startswith('SALVE obrigatoriamente')]
    return '\n'.join(lines).replace('(na pasta ./referencias/ e, quando anexadas, nesta mesma ordem)', '(anexadas nesta mesma ordem)') + GEMINI_WEB_SUFFIX


def codex_models() -> list[dict]:
    """Modelos que o próprio Codex lista para a conta (cache local dele); vazio se não houver."""
    cache = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')) / 'models_cache.json'
    try:
        models = json.loads(cache.read_text(encoding='utf-8')).get('models', [])
    except (OSError, ValueError, AttributeError):
        return []
    return [{'id': m['slug'], 'name': m.get('display_name') or m['slug']}
            for m in models if isinstance(m, dict) and m.get('slug') and m.get('visibility') == 'list']




class ProviderRegistry:
    def __init__(self, base: Path):
        self.base = base
        self.media = base / 'data' / 'media'
        self.jobs = base / 'data' / 'jobs'
        self.config = base / 'clients.json'
        # Experimental: sessão do gemini.google.com por biblioteca não oficial (gemini-webapi).
        self.gemini_cookies = base / 'gemini_cookies.json'
        self.gemini_lock = threading.Lock()   # um pedido por vez na mesma sessão, para não parecer robô
        self.chatgpt_web = ChatGPTWebClient(base)
        (self.media / 'frames').mkdir(parents=True, exist_ok=True)
        self.jobs.mkdir(parents=True, exist_ok=True)

    def configurations(self) -> list[dict]:
        configs = [
            {'id': 'demo', 'name': 'Demonstração (sem IA)', 'binary': '', 'note': 'Cria um rascunho ilustrativo; não usa IA.'},
            {'id': 'codex', 'name': 'OpenAI Codex CLI', 'binary': 'codex', 'note': 'Tenta usar $imagegen; depende da versão, conta e limites.',
             'models': codex_models(), 'efforts': EFFORTS},
            {'id': 'antigravity', 'name': 'Google Antigravity (agy)', 'binary': 'agy',
             'note': 'Usa a ferramenta de imagem do Antigravity; o serviço de imagem do Google pode estar instável.',
             'models': agy_models() if shutil.which('agy') else [], 'efforts': EFFORTS},
            {'id': 'gemini-web', 'name': 'Gemini no navegador (experimental)', 'binary': '',
             'note': 'Lê automaticamente a sessão do Gemini no navegador local. Entre em gemini.google.com neste computador; o login será verificado ao gerar. Integração não oficial e experimental.'},
            {'id': 'chatgpt-web', 'name': 'ChatGPT no navegador (experimental)', 'binary': '',
             'note': 'Gera em modo Chat no Chrome com sua sessão do ChatGPT. Requer a extensão oficial Playwright Bridge; autorize a conexão no navegador. Login e conexão são verificados ao gerar.'},
        ]
        if self.config.exists():
            try:
                custom = json.loads(self.config.read_text(encoding='utf-8'))
                for entry in custom:
                    if entry.get('id') not in {item['id'] for item in configs} and entry.get('command') and isinstance(entry['command'], list):
                        configs.append({'id': entry['id'], 'name': entry.get('name', entry['id']),
                                        'binary': entry['command'][0], 'command': entry['command'],
                                        'stdin': bool(entry.get('stdin')), 'note': entry.get('note', 'Cliente personalizado')})
            except (ValueError, KeyError, TypeError):
                pass
        for cfg in configs:
            cfg['available'] = (cfg['id'] == 'demo' or (cfg['id'] == 'gemini-web' and self.gemini_web_ready())
                                or (cfg['id'] == 'chatgpt-web' and self.chatgpt_web.available())
                                or bool(cfg['binary'] and shutil.which(cfg['binary'])))
            cfg.setdefault('models', [])
            cfg.setdefault('efforts', [])
        return configs

    def gemini_web_ready(self) -> bool:
        # Disponível para tentar gerar; não acessa cookies nem valida login ao listar o menu.
        if not importlib.util.find_spec('gemini_webapi'):
            return False
        return bool(importlib.util.find_spec('browser_cookie3') or self._gemini_manual_cookies())

    def _gemini_manual_cookies(self) -> dict:
        try:
            cookies = json.loads(self.gemini_cookies.read_text(encoding='utf-8'))
            psid = cookies.get('__Secure-1PSID', '')
            psidts = cookies.get('__Secure-1PSIDTS', '')
            if isinstance(psid, str) and psid.strip() and not psid.startswith('cole aqui'):
                return {'__Secure-1PSID': psid.strip(),
                        '__Secure-1PSIDTS': psidts.strip() if isinstance(psidts, str) else ''}
        except (OSError, ValueError, AttributeError):
            pass
        return {}

    def _gemini_web(self, prompt: str, refs: list[Path], job: Path) -> Path:
        # A biblioteca guarda os cookies renovados; por padrão em /tmp (legível por outros usuários), aqui em data/.
        cache = self.base / 'data' / 'gemini_cookie_cache'
        cache.mkdir(parents=True, exist_ok=True, mode=0o700)
        cache.chmod(0o700)
        os.environ['GEMINI_COOKIE_PATH'] = str(cache)
        from gemini_webapi import AuthError, GeminiClient, logger
        # A biblioteca pode incluir caminhos com cookies nos próprios erros de cache.
        logger.disable('gemini_webapi')
        cookies = self._gemini_manual_cookies()

        async def run() -> Path:
            # Sem valores explícitos, gemini-webapi usa browser-cookie3 com filtro google.com
            # e envia somente __Secure-1PSID e __Secure-1PSIDTS da sessão encontrada.
            client = GeminiClient(cookies.get('__Secure-1PSID'), cookies.get('__Secure-1PSIDTS') or None)
            try:
                await client.init(timeout=300, auto_close=False, auto_refresh=False, verbose=False)
                output = await client.generate_content(prompt, files=[str(path) for path in refs] or None)
                generated = output.candidates[output.chosen].generated_images
                if not generated:
                    raise GeminiWebError('O Gemini respondeu sem gerar imagem. Tente reformular o pedido ou confira o limite da sua conta.')
                return Path(await generated[0].save(path=str(job), filename='quadro.png', full_size=True))
            finally:
                await client.close()

        with self.gemini_lock:
            try:
                return asyncio.run(run())
            except AuthError:
                raise RuntimeError('Não foi possível autenticar no Gemini. Abra gemini.google.com no navegador deste computador, '
                                   'entre na conta e tente novamente. Se o perfil ou o chaveiro não estiver acessível, '
                                   'use gemini_cookies.json como alternativa.') from None
            except GeminiWebError:
                raise
            except Exception:
                # Não grava exceções externas com cookies/URLs no card ou no banco.
                raise RuntimeError('Falha ao acessar o Gemini ou baixar a imagem. Confira a conexão e a sessão no navegador e tente novamente.') from None
            finally:
                try:
                    for cached in cache.iterdir():
                        if cached.is_file():
                            cached.chmod(0o600)
                except OSError:
                    raise RuntimeError('Não foi possível proteger o cache local da sessão do Gemini.') from None

    def check_options(self, provider: dict, model: str, effort: str):
        """Só aceita modelo e esforço que o cliente oferece (vazio = padrão do próprio cliente)."""
        if model and model not in {m['id'] for m in provider['models']}:
            raise ValueError(f"Modelo '{model}' não está disponível para {provider['name']}.")
        if effort and effort not in provider['efforts']:
            raise ValueError(f"Esforço '{effort}' não está disponível para {provider['name']}.")

    def list_public(self):
        return [{k: v for k, v in cfg.items() if k not in ('command', 'stdin', 'binary')} for cfg in self.configurations()]

    def get(self, provider_id: str) -> dict:
        found = next((p for p in self.configurations() if p['id'] == provider_id), None)
        if not found:
            raise ValueError('Cliente de IA desconhecido. Configure-o em clients.json.')
        if not found['available']:
            if provider_id == 'chatgpt-web':
                raise ValueError('Instale o cliente com ./chatgpt-web.sh instalar. Requer Node.js 22 ou superior e Chrome.')
            if provider_id == 'gemini-web':
                raise ValueError('Instale as dependências com .venv/bin/python -m pip install -r requirements-experimental.txt '
                                 'e entre em gemini.google.com no navegador deste computador.')
            raise ValueError(f"O executável '{found['binary']}' não foi encontrado no PATH do servidor.")
        return found

    def generate(self, provider_id: str, prompt: str, references: list[tuple[Path, str]], frame_id: str,
                 model: str = '', effort: str = '', refine: bool = False) -> str:
        """`references` traz (arquivo, nome com o dono): o pedido cita cada foto por esse nome."""
        provider = self.get(provider_id)
        if provider_id == 'demo':
            return self._demo(prompt, frame_id)
        job = self.jobs / f'{frame_id}-{uuid.uuid4().hex[:8]}'
        job.mkdir(parents=True, exist_ok=False)
        try:
            copied = []
            refs_dir = job / 'referencias'
            refs_dir.mkdir()
            for source, name in references[:10]:
                if not source.is_file() or source.suffix.lower() not in SUPPORTED_SUFFIXES:
                    continue
                dest = refs_dir / Path(name).name
                shutil.copyfile(source, dest)
                copied.append(dest)
            final_prompt = prompt + '\n\nTrabalhe SOMENTE nesta pasta de execução. Se você não tiver uma ferramenta capaz de gerar uma imagem rasterizada, explique a limitação; não finja ter gerado a imagem.'
            if provider_id == 'antigravity':
                final_prompt += AGY_SUFFIX
            (job / 'brief.txt').write_text(final_prompt, encoding='utf-8')
            self.check_options(provider, model, effort)
            if provider_id == 'gemini-web':
                return self._store(self._gemini_web(gemini_web_prompt(prompt), copied, job))
            if provider_id == 'chatgpt-web':
                return self._store(self.chatgpt_web.generate(chatgpt_web_prompt(prompt), copied, frame_id, refine))
            command = self._command(provider, final_prompt, copied, job, model, effort)
            started = time.time() - 1
            proc = subprocess.run(command, cwd=job, input=final_prompt if provider.get('stdin') else None,
                                  capture_output=True, text=True, timeout=600, check=False)
            if proc.returncode != 0:
                detail = (proc.stderr or proc.stdout).strip()[-650:]
                raise RuntimeError(f'Cliente encerrou com código {proc.returncode}. {detail}')
            generated = next((job / ('quadro' + suffix) for suffix in SUPPORTED_SUFFIXES if (job / ('quadro' + suffix)).exists()), None)
            if generated is None and provider_id == 'antigravity':
                generated = antigravity_image(proc.stdout, started)
            if generated is None:
                # Alguns clientes não sabem gerar imagens; não confundimos resposta em texto com arquivo.
                detail = (proc.stdout or proc.stderr).strip()
                if provider_id == 'antigravity':
                    try:
                        detail = json.loads(detail.splitlines()[-1]).get('response', detail)
                    except (ValueError, IndexError, AttributeError):
                        pass
                detail = detail.strip()[-450:]
                raise RuntimeError('O cliente respondeu, mas não gerou quadro.png/.webp/.jpg. ' + detail)
            return self._store(generated)
        finally:
            shutil.rmtree(job, ignore_errors=True)

    def _store(self, generated: Path) -> str:
        """Confere que é mesmo uma imagem e copia para a mídia do app."""
        if generated.stat().st_size > 30 * 1024 * 1024:
            raise ValueError('A imagem gerada excedeu 30 MB.')
        suffix = file_type(generated)
        if not suffix:
            raise ValueError('O arquivo final não é uma imagem PNG, JPEG ou WebP válida.')
        name = f'{uuid.uuid4().hex}{suffix}'
        shutil.copyfile(generated, self.media / 'frames' / name)
        return f'/media/frames/{name}'

    def _command(self, provider: dict, prompt: str, refs: list[Path], cwd: Path, model: str = '', effort: str = '') -> list[str]:
        p = provider['id']
        if p == 'codex':
            command = ['codex', 'exec', '--skip-git-repo-check', '--sandbox', 'workspace-write', '--ephemeral']
            if model:
                command += ['-m', model]
            if effort:
                command += ['-c', f'model_reasoning_effort="{effort}"']
            if refs:
                command += ['--image', *(str(path) for path in refs)]
            # `--image` aceita vários valores seguidos: sem o `--`, o Codex lê o pedido como mais uma imagem.
            return command + ['--', '$imagegen\n' + prompt]
        if p == 'antigravity':
            # JSON para saber a conversa (é lá que a imagem fica); as fotos ficam em ./referencias, que é o espaço de trabalho.
            command = ['agy', '--output-format', 'json', '--print-timeout', '540s', '--mode', 'accept-edits']
            if model:
                command += ['--model', model]
            if effort:
                command += ['--effort', effort]
            return command + ['-p', prompt]
        variables = {'prompt': prompt, 'output': str(cwd / 'quadro.png'),
                     'workdir': str(cwd), 'references': ','.join(str(path) for path in refs)}
        return [arg.replace('{prompt}', variables['prompt'])
                   .replace('{output}', variables['output'])
                   .replace('{workdir}', variables['workdir'])
                   .replace('{references}', variables['references']) for arg in provider['command']]

    def _demo(self, prompt: str, frame_id: str) -> str:
        scene = re.split(r'Descrição d[oa] (?:quadro|capa):', prompt)[-1].split('\n')[0].strip()
        lines = textwrap.wrap(scene, width=43)[:6]
        name = uuid.uuid4().hex + '.svg'
        texts = ''.join(f'<text x="56" y="{240 + i*33}" font-family="sans-serif" font-size="21" fill="#192d37">{escape(line)}</text>' for i, line in enumerate(lines))
        artwork = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600" viewBox="0 0 900 600">
<rect width="900" height="600" fill="#f5ecdc"/><rect x="23" y="23" width="854" height="554" rx="18" fill="#fffaf1" stroke="#24333b" stroke-width="6"/>
<circle cx="165" cy="120" r="62" fill="#edb36c" stroke="#24333b" stroke-width="6"/><circle cx="142" cy="110" r="8"/><circle cx="182" cy="110" r="8"/><path d="M139 143 Q164 165 192 143" fill="none" stroke="#24333b" stroke-width="7"/>
<path d="M100 183 Q164 140 232 183 L265 230 L72 230Z" fill="#4f98aa" stroke="#24333b" stroke-width="5"/>
<rect x="40" y="240" width="820" height="252" rx="18" fill="#f2f4f0"/>{texts}
<rect x="45" y="518" width="300" height="36" rx="18" fill="#e9ddc7"/><text x="62" y="543" font-size="16" font-family="sans-serif" fill="#423627">RASCUNHO DEMO — NÃO É IA</text></svg>'''
        (self.media / 'frames' / name).write_text(artwork, encoding='utf-8')
        return f'/media/frames/{name}'
