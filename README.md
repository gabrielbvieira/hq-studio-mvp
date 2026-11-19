# HQ Studio — MVP local

Editor simples de histórias em quadrinhos com projetos, personagens persistentes e geração de imagens quadro a quadro por clientes de IA instalados no computador.

## Começar

Requisitos: **Python 3.10+** (recomendado 3.12+) e Linux/macOS/Windows.

```bash
cd hq-studio-mvp
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**No Linux, também pode simplesmente executar `./iniciar.sh`**, que prepara o ambiente e inicia o aplicativo.

Abra **http://127.0.0.1:8000**. Não é necessário configurar API nem ter cliente de IA para testar o fluxo: o modo **Demonstração (sem IA)** cria imagens de exemplo com a descrição de cada quadro.

## Fluxo

Na barra lateral, **HQs** abre a página com todas as HQs do projeto: abrir, editar título/roteiro/figurinos, exportar PDF ou excluir (a exclusão apaga quadros, imagens e versões da HQ, depois de uma confirmação que oferece exportar o PDF antes).

1. Crie um **projeto** (ex.: Especial de Natal) e escolha o **estilo padrão** das HQs. Cada HQ tem o próprio **estilo visual** (editável em Editar HQ) e usa a biblioteca do projeto; o padrão só vem preenchido nas novas.
2. Cadastre **personagens**, **objetos** e **locais**, com nome, aliases, descrições, personalidade, **o que nunca pode mudar**, **erros a evitar** e até 12 fotos PNG/JPG/WebP. A foto principal (estrela) vai primeiro para a IA; até 3 fotos por ficha são enviadas em cada quadro.
3. Crie quantas **HQs** quiser no projeto. Elas compartilham sua biblioteca de referências. Cada HQ pode ter um **roteiro e contexto** (do que se trata, tom, relações entre personagens), enviado à IA junto com cada quadro.
4. Cada **card** é um quadro ou a capa: escolha o tipo e o formato no próprio card, escreva o que acontece (falas entre aspas; por padrão a **IA desenha os balões**) e clique em **Gerar**. Ao gerar, a descrição dos **cards anteriores** vai junto como contexto da história, para a IA saber o que já aconteceu. Para corrigir, escreva em "O que mudar" e use **Refinar** (ex.: "o Rafa ficou gordinho demais"). Dá para anexar até 4 imagens por card: botão **Imagem**, **Colar**, Ctrl+V na descrição ou arrastar sobre o card. Elas vão para a IA como `anexo_1.png`... Na ficha de um personagem, colar adiciona a foto.
5. Escolha um cliente de IA no topo. Clique em **Gerar quadro**. Continue escrevendo enquanto outros quadros processam.
6. Quando um quadro acertar o visual de alguém, amplie-o e use **Aprovar visual**: o recorte vira foto da ficha e guia os próximos quadros.
7. Se preferir posicionar o texto você mesmo, escolha **Eu posiciono** no topo da HQ (vale para o projeto): as imagens passam a vir sem texto e, em **Balões e narração**, escreva falas, pensamentos, gritos e narração. Arraste cada balão na imagem, alargue pela borda direita e aponte o rabicho para quem fala. Os balões ficam por cima da imagem (não são desenhados pela IA), então dá para corrigir texto sem gerar de novo, e eles continuam no lugar quando o quadro é regerado. As falas também vão no pedido à IA, para acertar expressões e deixar espaço livre.
8. Um card do tipo **Capa** sai em formato retrato e com o título da HQ em destaque; use as setas do card para deixá-lo no começo. Cada quadro tem um **formato** (paisagem, retrato ou quadrado) que vale para a próxima imagem gerada.
9. **Créditos** cria a última página com os nomes da biblioteca. Você escreve o papel de cada um e o rodapé; nada é inventado pela IA.
10. **Exportar PDF** baixa a HQ com uma página por quadro, do tamanho de cada imagem, pronta para mandar no Slack. Quadros ainda sem imagem ficam de fora. No modo **Eu posiciono**, os balões vão desenhados no PDF.
11. Peça alterações na caixa "O que mudar" e clique em **Refinar** para tentar uma nova versão usando a imagem anterior como referência. O histórico permite restaurar versões.

As descrições são salvas automaticamente e a interface consulta os status da fila a cada dois segundos. São **duas execuções em paralelo**, com fila automática para as seguintes. A fila está **na memória**: ao reiniciar, tarefas interrompidas passam ao estado de erro e podem ser reenviadas.

## Clientes de IA

Ao lado de **Gerar com** dá para escolher o **modelo** e o **esforço** do agente (Codex e Antigravity). O padrão é **esforço baixo**: o agente só lê o pedido e chama o gerador de imagem, então raciocinar mais gasta tokens sem melhorar o desenho. A imagem em si tem custo fixo por imagem. A escolha fica salva por cliente neste navegador e vale só para o app; o `~/.codex/config.toml` não muda. "Modelo padrão" e "Esforço padrão" usam o que o cliente já tem configurado. Os modelos do Codex vêm da lista que ele mesmo guarda (`~/.codex/models_cache.json`).

O menu detecta executáveis disponíveis no `PATH` de **onde o servidor FastAPI está rodando**:

- **Codex CLI:** `codex exec` + instrução `$imagegen` + fotos relacionadas ao quadro. Exige versão/conta habilitada para gerar imagens.
- **ChatGPT no navegador (experimental):** usa `chatgpt-image-cli` para gerar em **modo Chat** na sua sessão do Chrome. Instale o cliente com `./chatgpt-web.sh instalar` (Node.js 22+ e npm), adicione a [extensão oficial Playwright Bridge](https://chromewebstore.google.com/detail/playwright-mcp-bridge/mmlmfjhmonkocbjadbfplnigmagldckm), entre em `chatgpt.com` no Chrome e execute `./chatgpt-web.sh conectar`, autorizando a conexão no navegador. Depois selecione **ChatGPT no navegador (experimental)** no app. O menu habilitado confirma a instalação local; login, extensão e anexos são conferidos durante o pedido.

  As fotos e anexos são enviados na mesma ordem do pedido. **Refinar** continua a última conversa deste quadro feita pelo ChatGPT; sem conversa anterior, abre uma nova e usa a imagem atual como referência. **Gerar** abre um pedido novo. Se houver demora ou falha de download, repetir o mesmo pedido retoma a tarefa existente sem reenviar o prompt. Pedidos e resultados ficam em `data/chatgpt_web`, fora do git; a cópia de trabalho é preservada para permitir a retomada. O app exibe mensagens próprias em português, sem erros brutos ou valores de sessão.

  Para evitar autorizações repetidas da extensão, você pode copiar o token da página de status dela e executar `./chatgpt-web.sh token`: a entrada fica oculta e o valor é salvo em arquivo local com permissão `600`. É opcional; nenhum cookie precisa ser copiado. `./chatgpt-web.sh diagnostico` verifica a instalação. A integração não oficial depende da interface do ChatGPT; CAPTCHA ou login pendente precisam ser resolvidos por você no navegador. O cliente é fixado na revisão `a03d08f9a754b6b1cadbf2f5c5d168d47d8fd90e` do [projeto original](https://github.com/mxzs123/chatgpt-image-cli), com adaptações locais em `scripts/chatgpt-cli.patch`: compositor atual, controles em português, download das imagens `blob:`, anexos montados dentro da página (a extensão não consegue anexar arquivos locais direto), confirmação de cada foto pelo nome, reaproveitamento da aba em branco e registro de tempo de cada passo em `data/chatgpt_web/timing.log`. O instalador aplica o patch antes de compilar e `scripts/patch_playwright_bridge.py` faz o grupo de abas da extensão se chamar **HQ Studio** e o ChatGPT trabalhar em **segundo plano**, sem tirar o foco da aba do app. Depois de baixar a imagem, a conversa é **excluída** no ChatGPT; o Refinar seguinte começa outra conversa levando a imagem atual do quadro.
- **Google Antigravity (`agy`):** `agy -p` com saída JSON. A ferramenta de imagem dele salva na pasta da conversa (`~/.gemini/antigravity-cli/brain/...`), então o app busca a imagem lá pelo `conversation_id`, sem liberar comandos de terminal. Precisa de login feito uma vez com `agy` no terminal. Em novembro de 2026 o serviço de imagem do Google respondia erro 500; quando voltar, deve funcionar sem mudanças.
- **Gemini no navegador (experimental):** usa a sua sessão do gemini.google.com pelas bibliotecas **não oficiais** `gemini-webapi` e `browser-cookie3`. Instale com `.venv/bin/python -m pip install -r requirements-experimental.txt`, reinicie o app e entre em **gemini.google.com no navegador deste computador**, usando o mesmo usuário que executa o app. Selecione **Gemini no navegador (experimental)** e clique em **Gerar quadro**. A sessão é lida automaticamente ao gerar, sem copiar cookies. O menu habilitado indica que as dependências estão instaladas; a autenticação é confirmada durante a geração. Um pedido por vez; as fotos do elenco vão anexadas.

  A leitura usa o filtro `google.com`; somente `__Secure-1PSID` e `__Secure-1PSIDTS` são usados na autenticação. A biblioteca procura os perfis padrão dos navegadores compatíveis (Chrome, Chromium, Brave, Edge, Firefox e outros). Perfis adicionais, navegadores em outro computador ou chaveiros bloqueados podem impedir a leitura. O cache renovado fica em `data/gemini_cookie_cache`, fora do git, com diretório `700` e arquivos `600`; valores de sessão e erros brutos da biblioteca não aparecem no card. A integração continua experimental e pode parar de funcionar quando o Google mudar o serviço.

  **Alternativa manual:** se o navegador não puder ser lido, copie `gemini_cookies.example.json` para `gemini_cookies.json` (fora do git), preencha `__Secure-1PSID` e `__Secure-1PSIDTS` de gemini.google.com (DevTools > Aplicativo > Cookies) e rode `chmod 600 gemini_cookies.json`. Um arquivo válido tem prioridade; remova-o para voltar à descoberta automática. Os cookies valem como senha da conta.
- **Demonstração:** cria um cartão SVG local, **sem nenhuma IA**, apenas para validar o editor.

Claude Code e Gemini CLI saíram do menu: o Claude Code não gera imagem sozinho e o Gemini CLI foi descontinuado pelo Google (o substituto é o Antigravity, acima). Um cliente que gere imagem pode ser cadastrado em `clients.json` (abaixo).

Uma resposta textual, por mais convincente, **não é considerada uma imagem gerada**. Se a IA não salvar um PNG/JPEG/WebP real, o quadro apresenta o erro e preserva a imagem anterior.

A autenticação e limites pertencem a cada cliente; **o app não garante uso gratuito, geração com a assinatura, suporte a imagens nem acesso universal**. Nenhuma chave de API é criada pelo projeto. Para evitar cobranças inesperadas, confira se seu CLI está autenticado no plano desejado e não com uma chave de API que cobre pelo uso.

### Outro cliente de terminal (extensível)

Copie `clients.example.json` para `clients.json`, alterando o comando:

```json
[
  {
    "id": "minha-ia",
    "name": "Minha IA",
    "command": ["meu-cliente", "--prompt", "{prompt}", "--output", "{output}"]
  }
]
```

A configuração é uma **lista de argumentos**, sem `shell=True`. Variáveis disponíveis: `{prompt}`, `{output}` (caminho absoluto `quadro.png`), `{workdir}`, `{references}` (caminhos separados por vírgula). Acrescente `"stdin": true` se o CLI receber o prompt pela entrada padrão. Reinicie o app após editar. O executável deve ser encontrado no `PATH` do servidor e **gerar a imagem rasterizada em `quadro.png`, `quadro.webp`, `quadro.jpg` ou `quadro.jpeg` na pasta de trabalho**. Nem todo cliente conversacional consegue isso sem ferramenta adicional.

**Segurança:** os clientes de IA são agentes externos executados com as permissões do seu usuário e alguns podem ler arquivos do computador. Use somente executáveis confiáveis, sem ativar `--yolo` ou permissões irrestritas. O Codex é iniciado no sandbox `workspace-write`; os outros clientes usam as permissões próprias. Esta aplicação é feita para rodar apenas em `127.0.0.1`, **sem autenticação**. Não a exponha à internet sem antes adicionar proteção de acesso e isolar os processos dos agentes.

## Arquitetura limpa, sem excesso de camadas

```text
domain/comics.py                    # Entidades e regras puras de elenco e prompts
application/
  protocols/                       # Contratos de persistência, arquivos, IA e PDF
  use_cases/
    generate_frame/                 # Fila, geração e refinamento
    manage_studio/                 # Projetos, HQs, fichas, quadros e versões
      protocols/requests.py        # Contratos de entrada e validações
  errors.py                        # Falhas sem códigos ou dependências HTTP
infra/
  repositories/sqlite_repository.py
  services/
    image_providers/               # Codex, Gemini, ChatGPT, Antigravity e demo
    media_storage.py               # Upload, resolução segura e remoção de arquivos
    image_files.py                 # Identificação de PNG, JPEG e WebP
    pdf_exporter.py                # Renderização do PDF
presentation/
  controllers/studio_controller.py # Rotas e respostas HTTP
  static/                          # HTML, JavaScript e CSS existentes
main/
  factories/studio_factory.py       # Montagem e injeção das dependências
  application.py                   # FastAPI, erros HTTP, arquivos estáticos e lifecycle
app/main.py                        # Mantém o comando uvicorn app.main:app
tests/                             # Comportamento e fronteiras de arquitetura
data/                              # SQLite, fotos, imagens e estado das integrações
```

Segue a estratégia do SOFT: controllers em `presentation`, operações em `application/use_cases`, adaptadores em `infra` e composição em `main/factories`. Os casos de uso dependem de contratos próprios, não de FastAPI, SQLite ou bibliotecas de IA. As factories escolhem as implementações. O servidor continua sendo FastAPI e os caminhos em `data/` continuam iguais.

Veja [docs/architecture.md](docs/architecture.md) para localizar uma mudança e entender as fronteiras. Os testes de arquitetura impedem imports das camadas externas no domínio e nos casos de uso.

## Testar

```bash
pip install pytest httpx
pytest -q
```

## Limites deste MVP

- Não há consistência visual perfeita garantida. O sistema reaproveita **fichas e imagens de referência**, mas o gerador redesenha cada quadro.
- O elenco automático usa nome e aliases mencionados na descrição; não infere pronomes. Ajuste pelo botão **Elenco** quando precisar.
- As fotos vão para a IA com o nome do dono (`rafa_1.png`, `regis_1.png`) e o pedido liga cada arquivo ao personagem, mas a fidelidade do rosto ainda depende do gerador.
- O modo demonstração não é um modelo artístico; o primeiro teste real deve ser com o Codex instalado e autenticado.
- Há capa, créditos e exportação em PDF (um quadro por página); diagramação de vários quadros por página fica para versões futuras.
- No PDF, os textos usam a Helvetica embutida (latin-1): acentos do português saem certos; emojis e símbolos raros viram "?".
- A fonte dos balões (Comic Neue) vem do Google Fonts; sem internet, o navegador usa uma fonte parecida do sistema.
- A fila é local e volátil, apropriada para uso pessoal.
