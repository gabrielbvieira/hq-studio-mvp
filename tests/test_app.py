import os
import tempfile
import time
from pathlib import Path

os.environ['HQ_HOME'] = tempfile.mkdtemp(prefix='hq-studio-tests-')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fluxo_projetos_hqs_quadros_e_versoes():
    r = client.post('/api/projects', json={'name':'Especial de Natal','style':'Caricato'})
    assert r.status_code == 201
    project = r.json()
    reference = client.post(f"/api/projects/{project['id']}/assets", data={
        'name':'Régis','aliases':'Reginho','kind':'character',
        'description':'Barba curta','personality':'Odeia o Natal'})
    assert reference.status_code == 201
    comic = client.post(f"/api/projects/{project['id']}/comics", json={'title':'Viagem constrangedora'}).json()
    comic2 = client.post(f"/api/projects/{project['id']}/comics", json={'title':'Outro Natal'}).json()
    assert len(client.get(f"/api/projects/{project['id']}/assets").json()) == 1
    assert comic2['project_id'] == comic['project_id']
    frame = client.post(f"/api/comics/{comic['id']}/frames").json()
    assert client.patch(f"/api/frames/{frame['id']}", json={'description':'Régis está dentro do carro'}).status_code == 200
    result = client.post(f"/api/frames/{frame['id']}/generate", json={'provider':'demo'})
    assert result.status_code == 202
    for _ in range(60):
        latest = client.get(f"/api/comics/{comic['id']}/frames").json()[0]
        if latest['status'] in ('done', 'error'):
            break
        time.sleep(0.05)
    assert latest['status'] == 'done', latest['message']
    assert latest['image_path'].endswith('.svg')
    assert len(client.get(f"/api/frames/{frame['id']}/versions").json()) == 1
    refine = client.post(f"/api/frames/{frame['id']}/generate", json={
        'provider':'demo','feedback':'Mais irritado','refine':True})
    assert refine.status_code == 202
    for _ in range(60):
        latest = client.get(f"/api/comics/{comic['id']}/frames").json()[0]
        if latest['status'] in ('done', 'error'):
            break
        time.sleep(0.05)
    # Em modo demo a tarefa pode ser instantânea; se ainda estiver processando, aguarde.
    for _ in range(60):
        if len(client.get(f"/api/frames/{frame['id']}/versions").json()) == 2:
            break
        time.sleep(0.05)
    assert len(client.get(f"/api/frames/{frame['id']}/versions").json()) == 2
    r = client.get('/api/providers')
    assert any(x['id'] == 'demo' and x['available'] for x in r.json())


def test_hq_com_roteiro_criacao_e_edicao():
    project = client.post('/api/projects', json={'name': 'Roteiros'}).json()
    comic = client.post(f"/api/projects/{project['id']}/comics",
                        json={'title': 'Ceia', 'context': 'Família reunida na noite de Natal.'}).json()
    assert comic['context'] == 'Família reunida na noite de Natal.'
    r = client.patch(f"/api/comics/{comic['id']}", json={'title': 'A ceia', 'context': 'Novo roteiro'})
    assert r.status_code == 200 and r.json()['title'] == 'A ceia' and r.json()['context'] == 'Novo roteiro'
    assert client.patch(f"/api/comics/{comic['id']}", json={'title': '   ', 'context': ''}).status_code == 422
    assert client.patch('/api/comics/nao-existe', json={'title': 'x'}).status_code == 404


def test_migra_banco_antigo_sem_coluna_de_roteiro(tmp_path):
    import sqlite3
    from infra.repositories.sqlite_repository import SQLiteRepository
    path = tmp_path / 'antigo.sqlite3'
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE comics (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, title TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        db.execute("INSERT INTO comics(id, project_id, title) VALUES ('c1', 'p1', 'Antiga')")
    repo = SQLiteRepository(path)
    assert repo.get_comic('c1')['context'] == ''


PNG = (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
       b'\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82')


def wait_frame(comic_id):
    for _ in range(100):
        frame = client.get(f"/api/comics/{comic_id}/frames").json()[0]
        if frame['status'] in ('done', 'error'):
            return frame
        time.sleep(0.05)
    return frame


def test_ficha_com_varias_fotos_edicao_e_exclusao():
    project = client.post('/api/projects', json={'name': 'Fotos'}).json()
    files = [('images', ('a.png', PNG, 'image/png')), ('images', ('b.png', PNG, 'image/png'))]
    asset = client.post(f"/api/projects/{project['id']}/assets", files=files,
                        data={'name': 'Rafa', 'kind': 'character', 'traits': 'não é gordo'}).json()
    assert len(asset['photos']) == 2 and asset['traits'] == 'não é gordo'
    assert asset['photos'][0]['image_path'] == asset['image_path']
    second = asset['photos'][1]
    asset = client.post(f"/api/assets/{asset['id']}/photos/{second['id']}/principal").json()
    assert asset['image_path'] == second['image_path'] and asset['photos'][0]['id'] == second['id']
    crop = client.post(f"/api/assets/{asset['id']}/photos", files={'image': ('c.png', PNG, 'image/png')},
                       data={'source': 'frame'}).json()
    assert len(crop['photos']) == 3 and any(p['source'] == 'frame' for p in crop['photos'])
    after = client.delete(f"/api/assets/{asset['id']}/photos/{second['id']}").json()
    assert len(after['photos']) == 2 and after['image_path'] != second['image_path']
    assert client.post(f"/api/assets/{asset['id']}/photos", files={'image': ('x.png', b'nada', 'image/png')}).status_code == 422
    edited = client.patch(f"/api/assets/{asset['id']}", json={'name': 'Rafa', 'avoid': 'barriga'}).json()
    assert edited['avoid'] == 'barriga'
    assert client.delete(f"/api/assets/{asset['id']}").status_code == 204
    assert client.get(f"/api/projects/{project['id']}/assets").json() == []


def test_pedido_usa_elenco_figurino_e_fotos_nomeadas():
    from app.main import service
    project = client.post('/api/projects', json={'name': 'Elenco'}).json()
    pid = project['id']
    rafa = client.post(f"/api/projects/{pid}/assets", files={'images': ('r.png', PNG, 'image/png')},
                       data={'name': 'Rafa', 'kind': 'character', 'aliases': 'Noel'}).json()
    mau = client.post(f"/api/projects/{pid}/assets", files={'images': ('m.png', PNG, 'image/png')},
                      data={'name': 'Maurício', 'kind': 'character'}).json()
    regis = client.post(f"/api/projects/{pid}/assets", data={'name': 'Régis', 'kind': 'character'}).json()
    comic = client.post(f"/api/projects/{pid}/comics", json={'title': 'Natal'}).json()
    assert client.put(f"/api/comics/{comic['id']}/costumes",
                      json={'costumes': {rafa['id']: 'roupa de Papai Noel'}}).json()['costumes'] == {rafa['id']: 'roupa de Papai Noel'}
    frame = client.post(f"/api/comics/{comic['id']}/frames").json()
    client.patch(f"/api/frames/{frame['id']}", json={'description': 'O Noel dirige e o Régis reclama'})
    cast = client.put(f"/api/frames/{frame['id']}/cast", json={'items': [
        {'asset_id': mau['id'], 'included': True, 'role': 'joga um teclado'},
        {'asset_id': regis['id'], 'included': False}]}).json()['cast']
    assert {c['asset_id'] for c in cast} == {mau['id'], regis['id']}

    seen = {}
    original = service.providers.generate
    def fake(provider_id, prompt, references, frame_id, **options):
        seen['prompt'], seen['names'] = prompt, [name for _, name in references]
        return original('demo', prompt, references, frame_id, **options)
    service.providers.generate = fake
    try:
        assert client.post(f"/api/frames/{frame['id']}/generate", json={'provider': 'demo'}).status_code == 202
        assert wait_frame(comic['id'])['status'] == 'done'
    finally:
        service.providers.generate = original
    assert sorted(seen['names']) == ['mauricio_1.png', 'rafa_1.png']
    assert 'Figurino nesta história: roupa de Papai Noel' in seen['prompt']
    assert 'Papel neste quadro: joga um teclado' in seen['prompt']
    assert 'Personagem: Régis' not in seen['prompt']


def test_baloes_salvos_validados_e_enviados_no_pedido():
    from app.main import service
    project = client.post('/api/projects', json={'name': 'Balões'}).json()
    rafa = client.post(f"/api/projects/{project['id']}/assets", data={'name': 'Rafa', 'kind': 'character'}).json()
    assert project['text_mode'] == 'ai'
    assert client.patch(f"/api/projects/{project['id']}/text-mode", json={'text_mode': 'editor'}).json()['text_mode'] == 'editor'
    assert client.patch(f"/api/projects/{project['id']}/text-mode", json={'text_mode': 'x'}).status_code == 422
    comic = client.post(f"/api/projects/{project['id']}/comics", json={'title': 'Fronteira'}).json()
    frame = client.post(f"/api/comics/{comic['id']}/frames").json()
    assert frame['balloons'] == []
    client.patch(f"/api/frames/{frame['id']}", json={'description': 'Rafa no carro'})
    balloons = [{'id': 'b1', 'type': 'caption', 'text': 'Na fronteira...', 'x': 2, 'y': 2, 'w': 30},
                {'id': 'b2', 'type': 'speech', 'text': 'Carga liberada!', 'speaker': rafa['id'], 'x': 55, 'y': 5, 'w': 30,
                 'tail': {'x': 50, 'y': 60}}]
    saved = client.put(f"/api/frames/{frame['id']}/balloons", json={'balloons': balloons}).json()
    assert [b['text'] for b in saved['balloons']] == ['Na fronteira...', 'Carga liberada!']
    assert saved['balloons'][1]['tail'] == {'x': 50, 'y': 60}
    assert client.get(f"/api/comics/{comic['id']}/frames").json()[0]['balloons'][0]['type'] == 'caption'
    assert client.put(f"/api/frames/{frame['id']}/balloons", json={'balloons': [{'id': 'x', 'type': 'grito'}]}).status_code == 422

    seen = {}
    original = service.providers.generate
    def fake(provider_id, prompt, references, frame_id, **options):
        seen['prompt'] = prompt
        return original('demo', prompt, references, frame_id, **options)
    service.providers.generate = fake
    try:
        client.post(f"/api/frames/{frame['id']}/generate", json={'provider': 'demo'})
        assert wait_frame(comic['id'])['status'] == 'done'
    finally:
        service.providers.generate = original
    assert '- Rafa (fala): Carga liberada!' in seen['prompt']
    assert '- Narração: Na fronteira...' in seen['prompt']
    assert 'Não escreva balões' in seen['prompt']


def test_anexos_do_quadro_vao_para_a_ia_com_nome_proprio():
    from app.main import service
    project = client.post('/api/projects', json={'name': 'Anexos'}).json()
    comic = client.post(f"/api/projects/{project['id']}/comics", json={'title': 'Anexos'}).json()
    frame = client.post(f"/api/comics/{comic['id']}/frames").json()
    client.patch(f"/api/frames/{frame['id']}", json={'description': 'O carro igual ao da foto'})
    with_one = client.post(f"/api/frames/{frame['id']}/attachments", files={'image': ('carro.png', PNG, 'image/png')}).json()
    assert len(with_one['attachments']) == 1
    extra = client.post(f"/api/frames/{frame['id']}/attachments", files={'image': ('b.png', PNG, 'image/png')}).json()['attachments'][1]
    for _ in range(2):
        client.post(f"/api/frames/{frame['id']}/attachments", files={'image': ('c.png', PNG, 'image/png')})
    assert client.post(f"/api/frames/{frame['id']}/attachments", files={'image': ('d.png', PNG, 'image/png')}).status_code == 422
    assert len(client.delete(f"/api/frames/{frame['id']}/attachments/{extra['id']}").json()['attachments']) == 3
    assert client.post(f"/api/frames/{frame['id']}/attachments", files={'image': ('x.png', b'texto', 'image/png')}).status_code == 422

    seen = {}
    original = service.providers.generate
    def fake(provider_id, prompt, references, frame_id, **options):
        seen['prompt'], seen['names'] = prompt, [name for _, name in references]
        return original('demo', prompt, references, frame_id, **options)
    service.providers.generate = fake
    try:
        client.post(f"/api/frames/{frame['id']}/generate", json={'provider': 'demo'})
        assert wait_frame(comic['id'])['status'] == 'done'
    finally:
        service.providers.generate = original
    assert seen['names'] == ['anexo_1.png', 'anexo_2.png', 'anexo_3.png']
    assert '1. anexo_1.png — imagem que o autor anexou' in seen['prompt']


def test_capa_creditos_formato_e_pdf():
    from app.main import service
    project = client.post('/api/projects', json={'name': 'PDF'}).json()
    pid = project['id']
    client.post(f"/api/projects/{pid}/assets", data={'name': 'Rafa', 'kind': 'character'})
    client.post(f"/api/projects/{pid}/assets", data={'name': 'Carro', 'kind': 'object'})
    comic = client.post(f"/api/projects/{pid}/comics", json={'title': 'O Senhor dos Presentes'}).json()
    cid = comic['id']
    assert client.get(f"/api/comics/{cid}/export.pdf").status_code == 422
    panel = client.post(f"/api/comics/{cid}/frames").json()
    cover = client.post(f"/api/comics/{cid}/frames", json={'kind': 'cover'}).json()
    credits = client.post(f"/api/comics/{cid}/frames", json={'kind': 'credits'}).json()
    frames = client.get(f"/api/comics/{cid}/frames").json()
    assert [f['kind'] for f in frames] == ['cover', 'panel', 'credits']
    assert cover['format'] == 'portrait' and panel['format'] == 'landscape'
    assert credits['credits']['lines'] == [{'name': 'Rafa', 'role': ''}]
    assert client.patch(f"/api/frames/{panel['id']}/format", json={'format': 'square'}).json()['format'] == 'square'
    saved = client.put(f"/api/frames/{credits['id']}/credits", json={'heading': 'Elenco', 'footer': 'Direção: Gabriel — o grande diretor',
        'lines': [{'name': 'Rafa', 'role': 'O Noel do Paraguai'}, {'name': ' ', 'role': ''}]}).json()['credits']
    assert saved['lines'] == [{'name': 'Rafa', 'role': 'O Noel do Paraguai'}]
    assert client.post(f"/api/frames/{credits['id']}/generate", json={'provider': 'demo'}).status_code == 422
    assert client.put(f"/api/frames/{panel['id']}/credits", json={}).status_code == 422

    seen = {}
    original = service.providers.generate
    def fake(provider_id, prompt, references, frame_id, **options):
        seen[frame_id] = prompt
        return original('demo', prompt, references, frame_id, **options)
    service.providers.generate = fake
    try:
        client.patch(f"/api/frames/{cover['id']}", json={'description': 'Rafa de Noel com o carro'})
        client.post(f"/api/frames/{cover['id']}/generate", json={'provider': 'demo'})
        assert wait_frame(cid)['status'] == 'done'
    finally:
        service.providers.generate = original
    assert 'CAPA' in seen[cover['id']] and '“O Senhor dos Presentes”' in seen[cover['id']]
    assert 'retrato' in seen[cover['id']]

    client.put(f"/api/frames/{panel['id']}/balloons", json={'balloons': [
        {'id': 'b', 'type': 'speech', 'text': 'Carga liberada…', 'x': 50, 'y': 5, 'w': 30, 'tail': {'x': 50, 'y': 60}}]})
    client.patch(f"/api/projects/{pid}/text-mode", json={'text_mode': 'editor'})
    r = client.get(f"/api/comics/{cid}/export.pdf")
    assert r.status_code == 200 and r.content.startswith(b'%PDF')
    assert r.headers['x-skipped-frames'] == '1'
    assert 'o-senhor-dos-presentes' in r.headers['content-disposition'] or 'o_senhor_dos_presentes' in r.headers['content-disposition']


def test_comando_do_codex_separa_imagens_do_pedido(tmp_path):
    from app.main import providers
    refs = [tmp_path / 'rafa_1.png', tmp_path / 'regis_1.png']
    command = providers._command({'id': 'codex'}, 'Rafa no carro', refs, tmp_path)
    image = command.index('--image')
    assert command[image + 1:image + 3] == [str(r) for r in refs]
    assert command[image + 3] == '--' and command[-1].endswith('Rafa no carro')


def test_card_vira_capa_e_volta_e_gera_com_contexto():
    from app.main import service
    project = client.post('/api/projects', json={'name': 'Cards'}).json()
    comic = client.post(f"/api/projects/{project['id']}/comics", json={'title': 'Cards'}).json()
    first = client.post(f"/api/comics/{comic['id']}/frames").json()
    second = client.post(f"/api/comics/{comic['id']}/frames").json()
    client.patch(f"/api/frames/{first['id']}", json={'description': 'Rafa sai do Paraguai'})
    client.patch(f"/api/frames/{second['id']}", json={'description': 'Régis reclama'})
    cover = client.patch(f"/api/frames/{first['id']}/kind", json={'kind': 'cover'}).json()
    assert cover['kind'] == 'cover' and cover['format'] == 'portrait'
    assert client.patch(f"/api/frames/{first['id']}/kind", json={'kind': 'panel'}).json()['format'] == 'landscape'
    credits = client.post(f"/api/comics/{comic['id']}/frames", json={'kind': 'credits'}).json()
    assert client.patch(f"/api/frames/{credits['id']}/kind", json={'kind': 'cover'}).status_code == 422
    seen = {}
    original = service.providers.generate
    def fake(provider_id, prompt, references, frame_id, **options):
        seen['prompt'] = prompt
        return original('demo', prompt, references, frame_id, **options)
    service.providers.generate = fake
    try:
        client.post(f"/api/frames/{second['id']}/generate", json={'provider': 'demo'})
        for _ in range(100):
            if 'prompt' in seen and client.get(f"/api/comics/{comic['id']}/frames").json()[1]['status'] == 'done':
                break
            time.sleep(0.05)
    finally:
        service.providers.generate = original
    assert '- Quadro 1: Rafa sai do Paraguai' in seen['prompt']


def test_modelo_e_esforco_validados_e_no_comando(tmp_path):
    from app.main import providers
    codex = {'id': 'codex', 'name': 'Codex', 'models': [{'id': 'gpt-x', 'name': 'X'}], 'efforts': ['low', 'high']}
    command = providers._command(codex, 'Rafa', [], tmp_path, 'gpt-x', 'low')
    assert command[command.index('-m') + 1] == 'gpt-x'
    assert 'model_reasoning_effort="low"' in command
    assert command.index('-c') < command.index('--')
    plain = providers._command(codex, 'Rafa', [], tmp_path)
    assert '-m' not in plain and '-c' not in plain
    providers.check_options(codex, '', '')
    for bad in [('outro', ''), ('', 'ultra')]:
        try:
            providers.check_options(codex, *bad)
            assert False, bad
        except ValueError:
            pass
    project = client.post('/api/projects', json={'name': 'Esforço'}).json()
    comic = client.post(f"/api/projects/{project['id']}/comics", json={'title': 'E'}).json()
    frame = client.post(f"/api/comics/{comic['id']}/frames").json()
    client.patch(f"/api/frames/{frame['id']}", json={'description': 'Cena'})
    r = client.post(f"/api/frames/{frame['id']}/generate", json={'provider': 'demo', 'effort': 'low'})
    assert r.status_code == 422 and 'Esforço' in r.json()['detail']
    demo = next(p for p in client.get('/api/providers').json() if p['id'] == 'demo')
    assert demo['models'] == [] and demo['efforts'] == []
    # Só entram clientes que geram imagem de verdade (Claude Code e Gemini CLI não geram).
    assert {p['id'] for p in client.get('/api/providers').json()} >= {'demo', 'codex'}
    assert not {'claude', 'gemini'} & {p['id'] for p in client.get('/api/providers').json()}
    assert 'antigravity' in {p['id'] for p in client.get('/api/providers').json()}


def test_antigravity_comando_e_imagem_na_pasta_da_conversa(tmp_path):
    import json, os
    from app.main import providers
    from infra.services.image_providers.provider_registry import antigravity_image
    agy = {'id': 'antigravity', 'name': 'Antigravity', 'models': [{'id': 'm', 'name': 'M'}], 'efforts': ['low']}
    command = providers._command(agy, 'Rafa', [], tmp_path, 'm', 'low')
    assert command[:3] == ['agy', '--output-format', 'json'] and command[-2:] == ['-p', 'Rafa']
    assert command[command.index('--model') + 1] == 'm' and command[command.index('--effort') + 1] == 'low'
    brain = tmp_path / 'brain'
    (brain / 'conv' / '.system_generated' / 'subagents').mkdir(parents=True)
    (brain / 'conv' / '.system_generated' / 'subagents' / 'sub.json').write_text('{}')
    (brain / 'sub' / 'artifacts').mkdir(parents=True)
    old = brain / 'conv' / 'antiga.png'
    old.write_bytes(PNG)
    os.utime(old, (1, 1))
    new = brain / 'sub' / 'artifacts' / 'gato.png'
    new.write_bytes(PNG)
    (brain / 'outra').mkdir()
    (brain / 'outra' / 'alheia.png').write_bytes(PNG)
    stdout = json.dumps({'conversation_id': 'conv', 'status': 'SUCCESS', 'response': 'ok'})
    assert antigravity_image(stdout, 100, tmp_path) == new
    assert antigravity_image('texto sem json', 100, tmp_path) is None


def test_gemini_no_navegador_experimental(tmp_path, monkeypatch):
    import json
    import importlib.util
    from infra.services.image_providers.provider_registry import ProviderRegistry, gemini_web_prompt
    # Este caso cobre o modo manual, mesmo quando a dependência automática está instalada.
    find_spec = importlib.util.find_spec
    monkeypatch.setattr(importlib.util, 'find_spec', lambda name: None if name == 'browser_cookie3' else find_spec(name))
    registry = ProviderRegistry(tmp_path)
    web = lambda: next(p for p in registry.configurations() if p['id'] == 'gemini-web')
    assert not web()['available']
    (tmp_path / 'gemini_cookies.json').write_text(json.dumps({'__Secure-1PSID': ''}))
    assert not web()['available']
    (tmp_path / 'gemini_cookies.json').write_text(json.dumps({'__Secure-1PSID': 'x', '__Secure-1PSIDTS': 'y'}))
    assert web()['available']
    prompt = gemini_web_prompt('Descrição do quadro: Rafa\nSALVE obrigatoriamente a imagem final como quadro.png')
    assert 'SALVE' not in prompt and 'Gere a imagem agora' in prompt
    seen = {}
    def fake(prompt, refs, job):
        seen['refs'] = [p.name for p in refs]
        out = job / 'quadro.png'
        out.write_bytes(PNG)
        return out
    monkeypatch.setattr(registry, '_gemini_web', fake)
    ref = tmp_path / 'r.png'
    ref.write_bytes(PNG)
    path = registry.generate('gemini-web', 'Descrição do quadro: Rafa', [(ref, 'rafa_1.png')], 'f1')
    assert path.startswith('/media/frames/') and path.endswith('.png')
    assert seen['refs'] == ['rafa_1.png']


def test_excluir_hq_apaga_quadros_e_imagens():
    from app.main import MEDIA
    project = client.post('/api/projects', json={'name': 'Excluir'}).json()
    keep = client.post(f"/api/projects/{project['id']}/comics", json={'title': 'Fica'}).json()
    comic = client.post(f"/api/projects/{project['id']}/comics", json={'title': 'Sai'}).json()
    frame = client.post(f"/api/comics/{comic['id']}/frames").json()
    client.patch(f"/api/frames/{frame['id']}", json={'description': 'Cena'})
    client.post(f"/api/frames/{frame['id']}/attachments", files={'image': ('a.png', PNG, 'image/png')})
    client.post(f"/api/frames/{frame['id']}/generate", json={'provider': 'demo'})
    done = wait_frame(comic['id'])
    files = [MEDIA / done['image_path'].removeprefix('/media/'), MEDIA / done['attachments'][0]['image_path'].removeprefix('/media/')]
    assert all(f.exists() for f in files)
    assert client.delete(f"/api/comics/{comic['id']}").status_code == 204
    assert not any(f.exists() for f in files)
    assert [c['id'] for c in client.get(f"/api/projects/{project['id']}/comics").json()] == [keep['id']]
    assert client.get(f"/api/comics/{comic['id']}/frames").status_code == 404
    assert client.delete(f"/api/comics/{comic['id']}").status_code == 404


def test_estilo_visual_por_hq():
    from app.main import service
    project = client.post('/api/projects', json={'name': 'Estilos', 'style': 'Mangá preto e branco'}).json()
    herdado = client.post(f"/api/projects/{project['id']}/comics", json={'title': 'Padrão'}).json()
    proprio = client.post(f"/api/projects/{project['id']}/comics", json={'title': 'Própria', 'style': 'Aquarela infantil'}).json()
    assert herdado['style'] == 'Mangá preto e branco' and proprio['style'] == 'Aquarela infantil'
    editado = client.patch(f"/api/comics/{herdado['id']}", json={'title': 'Padrão', 'style': 'Pixel art'}).json()
    assert editado['style'] == 'Pixel art'
    assert client.patch(f"/api/comics/{herdado['id']}", json={'title': 'Renomeada'}).json()['style'] == 'Pixel art'
    frame = client.post(f"/api/comics/{proprio['id']}/frames").json()
    client.patch(f"/api/frames/{frame['id']}", json={'description': 'Cena'})
    seen = {}
    original = service.providers.generate
    def fake(provider_id, prompt, references, frame_id, **options):
        seen['prompt'] = prompt
        return original('demo', prompt, references, frame_id, **options)
    service.providers.generate = fake
    try:
        client.post(f"/api/frames/{frame['id']}/generate", json={'provider': 'demo'})
        assert wait_frame(proprio['id'])['status'] == 'done'
    finally:
        service.providers.generate = original
    assert 'Estilo visual do projeto: Aquarela infantil' in seen['prompt'] or 'Estilo visual da HQ: Aquarela infantil' in seen['prompt']


def test_migra_estilo_do_projeto_para_hqs_antigas(tmp_path):
    import sqlite3
    from infra.repositories.sqlite_repository import SQLiteRepository
    path = tmp_path / 'antigo.sqlite3'
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE projects (id TEXT PRIMARY KEY, name TEXT NOT NULL, style TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        db.execute("CREATE TABLE comics (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, title TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        db.execute("INSERT INTO projects(id, name, style) VALUES ('p1', 'P', 'Noir')")
        db.execute("INSERT INTO comics(id, project_id, title) VALUES ('c1', 'p1', 'Antiga')")
    assert SQLiteRepository(path).get_comic('c1')['style'] == 'Noir'
