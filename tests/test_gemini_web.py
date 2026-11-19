import json
import sys
from types import SimpleNamespace

import pytest

from infra.services.image_providers.provider_registry import ProviderRegistry


def test_menu_automatico_nao_le_sessao(tmp_path, monkeypatch):
    monkeypatch.setattr('infra.services.image_providers.provider_registry.importlib.util.find_spec', lambda name: object())
    registry = ProviderRegistry(tmp_path)
    monkeypatch.setattr(registry, '_gemini_manual_cookies', lambda: pytest.fail('Menu leu cookies'))
    assert registry.gemini_web_ready()
    assert not registry.gemini_cookies.exists()


def test_dependencias_e_alternativa_manual(tmp_path, monkeypatch):
    registry = ProviderRegistry(tmp_path)
    installed = {'gemini_webapi'}
    monkeypatch.setattr('infra.services.image_providers.provider_registry.importlib.util.find_spec', lambda name: name in installed or None)
    assert not registry.gemini_web_ready()
    for invalid in ('{', '[]', '{"__Secure-1PSID": 123}', '{"__Secure-1PSID": "cole aqui…"}'):
        registry.gemini_cookies.write_text(invalid)
        assert not registry.gemini_web_ready()
    registry.gemini_cookies.write_text(json.dumps({'__Secure-1PSID': 'manual-test'}))
    assert registry.gemini_web_ready()
    installed.clear()
    assert not registry.gemini_web_ready()
    with pytest.raises(ValueError, match='requirements-experimental.txt'):
        registry.get('gemini-web')


@pytest.mark.parametrize('manual', [False, True])
@pytest.mark.parametrize('failure', ['', 'auth', 'network', 'no-image', 'download'])
def test_geracao_com_sessao_e_limpeza(tmp_path, monkeypatch, manual, failure):
    registry = ProviderRegistry(tmp_path)
    if manual:
        registry.gemini_cookies.write_text(json.dumps({'__Secure-1PSID': 'manual-test', '__Secure-1PSIDTS': 'ts-test'}))
    calls = {}
    cache = tmp_path / 'data' / 'gemini_cookie_cache'
    cache.mkdir(mode=0o755)
    cached = cache / 'session-test.json'
    cached.write_text('{}')
    cached.chmod(0o644)
    job = tmp_path / 'job'
    job.mkdir()
    reference = tmp_path / 'rafa.png'
    reference.write_bytes(b'reference-test')

    class AuthError(Exception):
        pass

    class Image:
        async def save(self, **options):
            calls['save'] = options
            if failure == 'download':
                raise RuntimeError('private-session-test')
            output = job / 'quadro.png'
            output.write_bytes(b'\x89PNG\r\n\x1a\nimage-test')
            return str(output)

    class Client:
        def __init__(self, psid, psidts):
            calls['cookies'] = (psid, psidts)

        async def init(self, **options):
            calls['init'] = options
            if failure == 'auth':
                raise AuthError('private-session-test')
            if failure == 'network':
                raise RuntimeError('private-session-test')

        async def generate_content(self, prompt, files):
            calls['generate'] = (prompt, files)
            return SimpleNamespace(chosen=0, candidates=[SimpleNamespace(
                generated_images=[] if failure == 'no-image' else [Image()])])

        async def close(self):
            calls['closed'] = True

    monkeypatch.setitem(sys.modules, 'gemini_webapi', SimpleNamespace(
        GeminiClient=Client, AuthError=AuthError,
        logger=SimpleNamespace(disable=lambda name: calls.update(log_disabled=name))))
    monkeypatch.setenv('GEMINI_COOKIE_PATH', str(tmp_path / 'unused'))
    if failure:
        with pytest.raises(RuntimeError) as error:
            registry._gemini_web('Gere Rafa', [reference], job)
        assert 'private-session-test' not in str(error.value)
        assert ('autenticar' if failure == 'auth' else 'sem gerar imagem' if failure == 'no-image' else 'Falha ao acessar') in str(error.value)
    else:
        result = registry._gemini_web('Gere Rafa', [reference], job)
        assert result.is_file()
        assert calls['generate'] == ('Gere Rafa', [str(reference)])
        assert calls['save'] == {'path': str(job), 'filename': 'quadro.png', 'full_size': True}
    assert calls['cookies'] == (('manual-test', 'ts-test') if manual else (None, None))
    assert calls['closed']
    assert calls['init']['verbose'] is False
    assert calls['init']['auto_refresh'] is False
    assert calls['log_disabled'] == 'gemini_webapi'
    assert cache.stat().st_mode & 0o777 == 0o700
    assert cached.stat().st_mode & 0o777 == 0o600
    if not manual:
        assert not registry.gemini_cookies.exists()
