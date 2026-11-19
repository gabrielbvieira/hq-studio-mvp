import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra.services.image_providers.chatgpt_web import ChatGPTWebClient, chatgpt_web_prompt
from infra.services.image_providers.provider_registry import ProviderRegistry


PNG = b'\x89PNG\r\n\x1a\nimage-test'


@pytest.fixture
def installed(tmp_path, monkeypatch):
    client = ChatGPTWebClient(tmp_path)
    client.cli.parent.mkdir(parents=True)
    client.cli.write_text('// test CLI')
    monkeypatch.setattr('infra.services.image_providers.chatgpt_web.shutil.which', lambda name: '/usr/bin/node' if name == 'node' else None)
    return client


def test_menu_e_prompt(tmp_path, installed):
    registry = ProviderRegistry(tmp_path)
    cfg = next(p for p in registry.list_public() if p['id'] == 'chatgpt-web')
    assert cfg['available'] and cfg['models'] == [] and cfg['efforts'] == []
    prompt = chatgpt_web_prompt('Estilo: realista\nSALVE obrigatoriamente quadro.png\nFotos (na pasta ./referencias/ e, quando anexadas, nesta mesma ordem)')
    assert 'SALVE' not in prompt and 'pasta' not in prompt
    assert 'Estilo: realista' in prompt and 'Gere a imagem agora' in prompt
    installed.cli.unlink()
    with pytest.raises(ValueError, match='chatgpt-web.sh instalar'):
        registry.get('chatgpt-web')


def cli_response(options, status='completed', outside=None):
    request = json.loads(Path(options['args'][-1]).read_text())
    image = Path(outside) if outside else Path(request['output_dir']) / 'image.png'
    if not outside:
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(PNG)
    result = {'task_id': request['task_id'], 'status': status, 'thread_id': 'thread-test',
              'images': [{'path': str(image)}], 'error': {'message': 'private-session-test'}}
    return request, SimpleNamespace(returncode=0 if status == 'completed' else 13, stdout=json.dumps(result))


def test_referencias_retomada_e_refinamento(tmp_path, installed, monkeypatch):
    registry = ProviderRegistry(tmp_path)
    ref = tmp_path / 'rafa.png'
    ref.write_bytes(PNG)
    calls = []

    deleted = []

    def run(args, **options):
        if 'delete' in args:
            deleted.append(args[args.index('--task-id') + 1])
            return SimpleNamespace(returncode=0, stdout=json.dumps({'status': 'ok', 'result': {'deleted': True}}))
        request, result = cli_response({'args': args}, 'timed_out' if not calls else 'completed')
        calls.append(request)
        assert options['env']['CHATGPT_IMAGE_HOME'] == str(installed.home / 'cli')
        assert options['capture_output'] and options['timeout'] > request['timeout_seconds']
        assert request['force_resubmit'] is False
        return result

    monkeypatch.setattr('infra.services.image_providers.chatgpt_web.subprocess.run', run)
    with pytest.raises(RuntimeError, match='retomar sem reenviar'):
        registry.generate('chatgpt-web', 'Desenhe Rafa', [(ref, 'rafa_1.png')], 'frame-1')
    assert not list(registry.jobs.iterdir())
    assert Path(calls[0]['reference_images'][0]).read_bytes() == PNG
    image = registry.generate('chatgpt-web', 'Desenhe Rafa', [(ref, 'rafa_1.png')], 'frame-1')
    assert image.startswith('/media/frames/') and image.endswith('.png')
    assert (registry.media / image.removeprefix('/media/')).read_bytes() == PNG
    assert calls[0] == calls[1]  # Mesmo pedido persistido, sem depender da pasta temporária já apagada.
    assert deleted == [calls[1]['task_id']]   # conversa apagada logo depois de baixar a imagem
    registry.generate('chatgpt-web', 'Mais luz', [(ref, 'rafa_1.png')], 'frame-1', refine=True)
    # A conversa já foi apagada: o Refinar começa outra (a imagem atual vai como referência).
    assert calls[2]['mode'] == 'new' and 'thread_id' not in calls[2]
    assert calls[2]['task_id'] != calls[1]['task_id']
    registry.generate('chatgpt-web', 'Cena nova', [], 'frame-1')
    assert calls[3]['mode'] == 'new' and 'thread_id' not in calls[3]
    assert installed.home.stat().st_mode & 0o777 == 0o700
    assert all(path.stat().st_mode & 0o777 == 0o600 for path in (installed.home / 'frames').glob('*.json'))


@pytest.mark.parametrize('status, message', [
    ('login_required', 'Entre na sua conta'),
    ('human_action_required', 'intervenção'),
    ('content_blocked', 'não aceitou'),
    ('download_failed', 'download não terminou'),
    ('ui_changed', 'interface atual'),
    ('failed', 'Não foi possível concluir'),
])
def test_falhas_sem_expor_dados(installed, monkeypatch, status, message):
    monkeypatch.setattr('infra.services.image_providers.chatgpt_web.subprocess.run', lambda args, **kw: cli_response({'args': args}, status)[1])
    with pytest.raises(RuntimeError, match=message) as error:
        installed.generate('Imagem', [], 'frame')
    assert 'private-session-test' not in str(error.value)


def test_saida_fora_do_pedido_rejeitada(tmp_path, installed, monkeypatch):
    outside = tmp_path / 'outside.png'
    outside.write_bytes(PNG)
    monkeypatch.setattr('infra.services.image_providers.chatgpt_web.subprocess.run', lambda args, **kw: cli_response({'args': args}, outside=outside)[1])
    with pytest.raises(RuntimeError, match='pasta do pedido'):
        installed.generate('Imagem', [], 'frame')


def test_timeout_e_resposta_invalida_preservam_pedido(installed, monkeypatch):
    requests = []
    def run(args, **kw):
        requests.append(json.loads(Path(args[-1]).read_text()))
        if len(requests) == 1:
            raise subprocess.TimeoutExpired(args, kw['timeout'], output='private-session-test')
        return SimpleNamespace(returncode=1, stdout='private-session-test')
    monkeypatch.setattr('infra.services.image_providers.chatgpt_web.subprocess.run', run)
    for _ in range(2):
        with pytest.raises(RuntimeError, match='preservado') as error:
            installed.generate('Imagem', [], 'frame')
        assert 'private-session-test' not in str(error.value)
    assert requests[0] == requests[1]


def test_token_local_nao_vai_no_pedido(installed, monkeypatch):
    installed.home.mkdir(parents=True)
    token = installed.home / 'bridge-token'
    token.write_text('private-token-test')
    def run(args, **kw):
        assert kw['env']['PLAYWRIGHT_MCP_EXTENSION_TOKEN'] == 'private-token-test'
        assert 'private-token-test' not in Path(args[-1]).read_text()
        return cli_response({'args': args})[1]
    monkeypatch.setattr('infra.services.image_providers.chatgpt_web.subprocess.run', run)
    installed.generate('Imagem', [], 'frame')
    assert token.stat().st_mode & 0o777 == 0o600


def test_referencia_grande_vira_jpeg_menor(tmp_path):
    from PIL import Image
    from infra.services.image_providers.chatgpt_web import compact_reference
    big = tmp_path / 'quadro_atual.png'
    Image.new('RGB', (3000, 2000), (200, 30, 40)).save(big)
    small = tmp_path / 'rafa_1.png'
    small.write_bytes(PNG)
    out = tmp_path / 'out'
    out.mkdir()
    reduced = compact_reference(big, out)
    assert reduced.name == 'quadro_atual.jpg'
    with Image.open(reduced) as image:
        assert max(image.size) == 1536 and image.format == 'JPEG'
    kept = compact_reference(small, out)
    assert kept.name == 'rafa_1.png' and kept.read_bytes() == PNG


def test_falha_ao_apagar_conversa_nao_perde_a_imagem(tmp_path, installed, monkeypatch):
    registry = ProviderRegistry(tmp_path)
    calls = []

    def run(args, **options):
        if 'delete' in args:
            return SimpleNamespace(returncode=1, stdout='{"status": "error"}')
        request, result = cli_response({'args': args})
        calls.append(request)
        return result

    monkeypatch.setattr('infra.services.image_providers.chatgpt_web.subprocess.run', run)
    image = registry.generate('chatgpt-web', 'Desenhe Rafa', [], 'frame-2')
    assert image.startswith('/media/frames/')
    registry.generate('chatgpt-web', 'Mais luz', [], 'frame-2', refine=True)
    assert calls[1]['mode'] == 'continue' and calls[1]['thread_id'] == 'thread-test'   # chat ficou: continua nele
