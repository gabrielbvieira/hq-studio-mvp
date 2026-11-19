#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(dirname "$0")"
base="$PWD"
tool_dir="$base/data/tools/chatgpt-image-cli"
revision="a03d08f9a754b6b1cadbf2f5c5d168d47d8fd90e"
export CHATGPT_IMAGE_HOME="$base/data/chatgpt_web/cli"
export NO_UPDATE_NOTIFIER=1
export PLAYWRIGHT_MCP_TAB_GROUP_TITLE='HQ Studio'
export PLAYWRIGHT_MCP_TAB_GROUP_COLOR='purple'
export PLAYWRIGHT_MCP_BACKGROUND=1
mkdir -p "$base/data/chatgpt_web"
chmod 700 "$base/data/chatgpt_web"
if [[ -f "$base/data/chatgpt_web/bridge-token" ]]; then
  chmod 600 "$base/data/chatgpt_web/bridge-token"
  export PLAYWRIGHT_MCP_EXTENSION_TOKEN
  PLAYWRIGHT_MCP_EXTENSION_TOKEN="$(cat "$base/data/chatgpt_web/bridge-token")"
fi

case "${1:-ajuda}" in
  instalar)
    node -e 'if (Number(process.versions.node.split(".")[0]) < 22) { console.error("Instale Node.js 22 ou superior."); process.exit(1); }'
    if [[ ! -d "$tool_dir/.git" ]]; then
      mkdir -p "$tool_dir"
      git -C "$tool_dir" init -q
      git -C "$tool_dir" remote add origin https://github.com/mxzs123/chatgpt-image-cli.git
      git -C "$tool_dir" fetch --depth 1 origin "$revision"
      git -C "$tool_dir" checkout --detach -q FETCH_HEAD
    fi
    if [[ "$(git -C "$tool_dir" rev-parse HEAD)" != "$revision" ]]; then
      echo 'A ferramenta local está em outra revisão. Instalação interrompida para preservar os arquivos existentes.' >&2
      exit 1
    fi
    npm --prefix "$tool_dir" ci --ignore-scripts --no-audit --no-fund --cache "$base/data/npm-cache"
    # Adaptações locais (compositor atual, português, anexos pela página, tempos, aba em branco) num patch só.
    if git -C "$tool_dir" apply --check "$base/scripts/chatgpt-cli.patch" 2>/dev/null; then
      git -C "$tool_dir" apply "$base/scripts/chatgpt-cli.patch"
    elif ! git -C "$tool_dir" apply --reverse --check "$base/scripts/chatgpt-cli.patch" 2>/dev/null; then
      echo 'As adaptações locais não se aplicam a esta cópia da ferramenta. Instalação interrompida.' >&2
      exit 1
    fi
    python3 "$base/scripts/patch_playwright_bridge.py"
    npm --prefix "$tool_dir" run build
    echo 'Cliente instalado. Instale a extensão Playwright Bridge no Chrome e entre em chatgpt.com.'
    ;;
  conectar)
    cd "$base/data/chatgpt_web"
    node "$tool_dir/dist/cli.js" connect --session hq-studio
    ;;
  diagnostico)
    cd "$base/data/chatgpt_web"
    node "$tool_dir/dist/cli.js" doctor
    ;;
  token)
    python3 - <<'PY'
from getpass import getpass
from pathlib import Path
token = getpass('Token da extensão Playwright Bridge (entrada oculta): ').strip()
if not token:
    raise SystemExit('Nenhum token informado; configuração preservada.')
path = Path('data/chatgpt_web/bridge-token')
with path.open('w', encoding='utf-8') as output:
    path.chmod(0o600)
    output.write(token)
print('Token salvo localmente. Reiniciar o servidor não é necessário.')
PY
    ;;
  *)
    echo 'Uso: ./chatgpt-web.sh instalar | conectar | diagnostico | token'
    ;;
esac
