from domain.comics import Reference, mentioned_references, prepare_brief


def test_detecta_nomes_e_aliases_sem_falsos_positivos():
    refs = [Reference('1', 'Régis', 'character', aliases='Reginho'),
            Reference('2', 'Ana', 'character'),
            Reference('3', 'Sofá', 'object')]
    assert [r.name for r in mentioned_references('REGINHO está no sofá, com uma banana.', refs)] == ['Régis', 'Sofá']


def test_brief_com_feedback_sem_baloes():
    brief = prepare_brief('Régis no carro', 'Estilo cartoon', [Reference('1', 'Régis', 'character', personality='rabugento')],
                          'mais irritado', True)
    assert 'mais irritado' in brief
    assert 'rabugento' in brief
    assert 'Não escreva balões' in brief
    assert 'quadro.png' in brief


def test_brief_inclui_roteiro_da_hq_antes_do_quadro():
    brief = prepare_brief('Régis abre o presente', 'Cartoon', [], comic_title='Amigo secreto',
                          comic_context='Régis odeia o Natal, mas a família insiste no amigo secreto.')
    assert 'Amigo secreto' in brief
    assert 'odeia o Natal' in brief
    assert brief.index('odeia o Natal') < brief.index('Descrição do quadro: Régis abre o presente')


def test_brief_sem_roteiro_nao_cria_secao_vazia():
    assert 'ROTEIRO' not in prepare_brief('Cena', 'Cartoon', [])


def test_elenco_soma_citados_e_inclusoes_e_tira_removidos():
    from domain.comics import CastEntry, resolve_cast
    refs = [Reference('1', 'Rafa', 'character', aliases='Noel'),
            Reference('2', 'Maurício', 'character', aliases='Mauricião'),
            Reference('3', 'Régis', 'character'),
            Reference('4', 'Carro', 'object')]
    cast = resolve_cast('O Noel dirige o carro enquanto Régis observa', refs,
                        [CastEntry('2', True, 'atacando com periféricos'), CastEntry('3', False)])
    assert [a.name for a in cast] == ['Rafa', 'Maurício', 'Carro']
    assert cast[1].role == 'atacando com periféricos'


def test_fotos_recebem_nome_do_dono_e_dividem_o_limite():
    from domain.comics import assign_reference_files
    refs = [Reference('1', 'Rafa', 'character', photos=('a.png', 'b.jpg', 'c.png', 'd.png')),
            Reference('2', 'Régis', 'character', photos=('e.webp',)),
            Reference('3', 'Rafa', 'character', photos=('f.png',))]
    cast, plan = assign_reference_files(refs, lambda p: '.' + p.split('.')[-1], budget=4)
    assert plan == [('a.png', 'rafa_1.png'), ('e.webp', 'regis_1.webp'), ('f.png', 'rafa2_1.png'), ('b.jpg', 'rafa_2.jpg')]
    assert cast[0].files == ('rafa_1.png', 'rafa_2.jpg')


def test_brief_liga_cada_foto_ao_personagem_com_papel_e_figurino():
    ref = Reference('1', 'Rafa', 'character', traits='rosto redondo, não é gordo', avoid='barriga grande',
                    costume='roupa de Papai Noel', role='dirigindo o carro', files=('rafa_1.png', 'rafa_2.png'))
    brief = prepare_brief('Rafa na estrada', 'Semirrealista', [ref], previous_file='quadro_atual.png', has_previous=True)
    assert 'Papel neste quadro: dirigindo o carro' in brief
    assert 'Figurino nesta história: roupa de Papai Noel' in brief
    assert 'Nunca pode mudar: rosto redondo, não é gordo' in brief
    assert 'Evite: barriga grande' in brief
    assert '1. rafa_1.png — foto de Rafa' in brief
    assert '3. quadro_atual.png — versão atual deste quadro' in brief
    assert 'REGRAS DE IDENTIDADE' in brief


def test_brief_sem_personagens_nao_traz_regras_de_identidade():
    assert 'REGRAS DE IDENTIDADE' not in prepare_brief('Estrada vazia', 'Cartoon', [Reference('1', 'Estrada', 'location')])


def test_falas_viram_roteiro_no_pedido_sem_pedir_texto_na_imagem():
    from domain.comics import dialogue_lines
    lines = dialogue_lines([
        {'type': 'caption', 'text': 'Em algum lugar da fronteira...'},
        {'type': 'speech', 'speaker': 'r', 'text': 'Carga liberada!'},
        {'type': 'shout', 'speaker': 'x', 'text': 'NÃO!'},
        {'type': 'thought', 'speaker': 'r', 'text': '   '},
    ], {'r': 'Rafa'})
    assert lines == ['Narração: Em algum lugar da fronteira...', 'Rafa (fala): Carga liberada!', 'Alguém (grita): NÃO!']
    brief = prepare_brief('Rafa dirige', 'HQ', [], dialogue=lines)
    assert 'para 3 balões' in brief and '- Rafa (fala): Carga liberada!' in brief
    assert 'Não escreva balões' in brief
    assert 'TEXTO DESTE QUADRO' not in prepare_brief('Rafa dirige', 'HQ', [])


def test_modo_ia_pede_baloes_desenhados_com_as_falas_do_autor():
    brief = prepare_brief('Rafa diz "Carga liberada!"', 'HQ', [], ai_text=True, dialogue=['Rafa (fala): Bora!'])
    assert 'DESENHE os balões' in brief and 'Não escreva balões' not in brief
    assert 'TEXTO PARA OS BALÕES DESTE QUADRO' in brief and '- Rafa (fala): Bora!' in brief


def test_contexto_traz_cards_anteriores_em_ordem_sem_creditos():
    from domain.comics import previous_context
    frames = [{'position': 1, 'kind': 'cover', 'description': 'Capa épica'},
              {'position': 2, 'kind': 'panel', 'description': 'Rafa   sai do Paraguai'},
              {'position': 3, 'kind': 'panel', 'description': ''},
              {'position': 4, 'kind': 'panel', 'description': 'Régis reclama'},
              {'position': 5, 'kind': 'credits', 'description': ''}]
    assert previous_context(frames, 4) == ['Capa: Capa épica', 'Quadro 2: Rafa sai do Paraguai']
    brief = prepare_brief('Régis reclama', 'HQ', [], previous_frames=previous_context(frames, 4))
    assert brief.index('CARDS ANTERIORES') < brief.index('Descrição do quadro: Régis reclama')
    assert 'CARDS ANTERIORES' not in prepare_brief('x', 'HQ', [])
