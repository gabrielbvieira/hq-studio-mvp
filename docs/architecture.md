# Organização do código

O HQ Studio separa a interface HTTP, os casos de uso, as regras de domínio e as integrações externas. Os controllers ficam em `presentation/controllers`, as operações em `application/use_cases` e os adaptadores em `infra`. As factories em `main/factories` conectam essas camadas. O servidor usa FastAPI e a persistência local usa SQLite.

## Fluxo de uma requisição

1. `presentation/controllers/studio_controller.py` recebe os parâmetros e converte resultados para HTTP. Não acessa SQLite nem instancia clientes de IA.
2. `application/use_cases/manage_studio/manage_studio.py` valida regras e coordena projetos, HQs, fichas, anexos, balões e versões. Erros de aplicação não conhecem códigos HTTP.
3. `application/use_cases/generate_frame/generate_frame.py` controla a fila e prepara referências e contexto para gerar ou refinar um quadro.
4. `domain/comics.py` resolve elenco, nomes, aliases, limites de quantidade e montagem dos prompts. Usa apenas a biblioteca padrão do Python.
5. `application/protocols` descreve os contratos que os adaptadores implementam: repositório, arquivos, provedores e exportação.
6. `main/factories/studio_factory.py` injeta `SQLiteRepository`, `LocalMediaStorage`, `ProviderRegistry` e o exportador PDF nos casos de uso. É o ponto que conhece as implementações concretas.

`main/application.py` monta o servidor, registra a tradução dos erros para 404/409/422, publica os arquivos estáticos e fecha o executor ao encerrar a aplicação. `create_app(base)` permite montar instâncias isoladas em diretórios temporários. `app/main.py` mantém o comando de execução existente.

## Onde fazer cada mudança

| Mudança | Local |
| --- | --- |
| Regra de nomes, elenco ou conteúdo do prompt | `domain/comics.py` |
| Operação de projeto, HQ, personagem ou quadro | `application/use_cases/manage_studio` |
| Geração, fila e refinamento | `application/use_cases/generate_frame` |
| Contrato de dependência substituível | `application/protocols` |
| Campos e validações das entradas | `application/use_cases/manage_studio/protocols/requests.py` |
| Rota, status ou resposta HTTP | `presentation/controllers/studio_controller.py` |
| Interface do usuário | `presentation/static` |
| SQL e persistência | `infra/repositories/sqlite_repository.py` |
| Uploads e arquivos | `infra/services/media_storage.py` |
| Integração com IA | `infra/services/image_providers` |
| Renderização de PDF | `infra/services/pdf_exporter.py` |
| Seleção das implementações concretas | `main/factories/studio_factory.py` |
| Inicialização e ciclo de vida | `main/application.py` |

## Dados e dependências

`HQ_HOME` aponta para a raiz dos dados de execução, enquanto os arquivos estáticos vêm da raiz do código. O diretório `data/` armazena o banco SQLite, as imagens geradas e o estado das integrações com o navegador.

Os contratos de entrada usam Pydantic para validar os dados. Os casos de uso não importam FastAPI; a apresentação traduz suas falhas para HTTP. As operações são agrupadas por responsabilidade: gerenciamento do estúdio e geração de quadros.

## Validação

Execute `.venv/bin/python -m pytest -q`. Os testes existentes verificam os fluxos do produto; `tests/test_architecture.py` verifica a direção dos imports, a independência do domínio, o isolamento das factories e a publicação da interface. Os testes usam dados temporários e não iniciam o servidor de uso local.
