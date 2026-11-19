"""Ajustes no Playwright para a extensão Playwright Bridge. Pode rodar de novo (não duplica nada).

- Grupo de abas: a extensão aceita `tabGroupTitle`/`tabGroupColor` na página de conexão, mas esta versão
  do Playwright não os envia (o grupo fica "Playwright · playwright-cli"). Com PLAYWRIGHT_MCP_TAB_GROUP_TITLE
  e PLAYWRIGHT_MCP_TAB_GROUP_COLOR, o grupo ganha o nome e a cor escolhidos.
- Segundo plano: com PLAYWRIGHT_MCP_BACKGROUND=1, conecta sem focar a janela, abre abas sem ativá-las e
  troca de aba sem trazê-la para a frente. Assim quem está usando o HQ Studio não perde a aba.
"""
from pathlib import Path

bundle = (Path(__file__).resolve().parent.parent
          / 'data/tools/chatgpt-image-cli/node_modules/playwright-core/lib/coreBundle.js')
source = bundle.read_text(encoding='utf-8')
connect = 'url3.searchParams.set("protocolVersion", this._protocolVersion.toString());'

patches = [
    # (já aplicado se contém, trecho original, trecho novo)
    ('PLAYWRIGHT_MCP_TAB_GROUP_TITLE', connect,
     connect + '\n        if (process.env.PLAYWRIGHT_MCP_TAB_GROUP_TITLE)'
     '\n          url3.searchParams.set("tabGroupTitle", process.env.PLAYWRIGHT_MCP_TAB_GROUP_TITLE);'
     '\n        if (process.env.PLAYWRIGHT_MCP_TAB_GROUP_COLOR)'
     '\n          url3.searchParams.set("tabGroupColor", process.env.PLAYWRIGHT_MCP_TAB_GROUP_COLOR);'),
    ('searchParams.set("background"', connect,
     connect + '\n        if (process.env.PLAYWRIGHT_MCP_BACKGROUND)'
     '\n          url3.searchParams.set("background", "true");'),
    ('active: process.env.PLAYWRIGHT_MCP_BACKGROUND',
     'this._sendToExtension("chrome.tabs.create", [{ url: url3 }]);',
     'this._sendToExtension("chrome.tabs.create", [{ url: url3, active: process.env.PLAYWRIGHT_MCP_BACKGROUND ? false : void 0 }]);'),
    ('if (!process.env.PLAYWRIGHT_MCP_BACKGROUND) await tab2.page.bringToFront();',
     'await tab2.page.bringToFront();',
     'if (!process.env.PLAYWRIGHT_MCP_BACKGROUND) await tab2.page.bringToFront();'),
]
for done, marker, replacement in patches:
    if done in source:
        continue
    if source.count(marker) != 1:
        raise SystemExit(f'Versão do Playwright diferente da esperada; ajuste não aplicado: {marker[:60]}')
    source = source.replace(marker, replacement)
bundle.write_text(source, encoding='utf-8')
