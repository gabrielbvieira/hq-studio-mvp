"""Entidades e regras puras. Sem FastAPI, SQL ou dependências de IA."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace

KIND_LABELS = {'character': 'Personagem', 'object': 'Objeto', 'location': 'Local'}
MAX_REFERENCE_IMAGES = 10
MAX_ATTACHMENTS = 4
MAX_PHOTOS = 12
FORMATS = {
    'landscape': 'paisagem, mais larga que alta (proporção 3:2, como um quadro de HQ)',
    'portrait': 'retrato, mais alta que larga (proporção 2:3, como uma página ou capa)',
    'square': 'quadrada (1:1)',
}
PHOTOS_PER_REFERENCE = 3


@dataclass(frozen=True)
class Reference:
    id: str
    name: str
    kind: str
    description: str = ""
    personality: str = ""
    aliases: str = ""
    image_path: str | None = None
    traits: str = ""                 # o que nunca pode mudar (rosto, corpo, marcas)
    avoid: str = ""                  # erros que a IA já cometeu e não deve repetir
    photos: tuple[str, ...] = ()     # fotos da ficha, a principal primeiro
    costume: str = ""                # figurino só nesta HQ
    role: str = ""                   # papel só neste quadro
    files: tuple[str, ...] = ()      # nomes das fotos enviadas à IA neste quadro


@dataclass(frozen=True)
class CastEntry:
    """Ajuste manual do elenco de um quadro: incluir/remover e o papel na cena."""
    asset_id: str
    included: bool = True
    role: str = ""


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    return "".join(ch for ch in value if not unicodedata.combining(ch))


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", normalize(value)).strip("_") or "referencia"


def mentioned_references(description: str, assets: list[Reference]) -> list[Reference]:
    """Detecta nomes/aliases completos, sem confundir 'Ana' com 'banana'."""
    desc = normalize(description)
    found: list[Reference] = []
    for asset in assets:
        names = [asset.name, *asset.aliases.split(",")]
        for name in names:
            candidate = normalize(name.strip())
            if candidate and re.search(r"(?<!\w)" + re.escape(candidate) + r"(?!\w)", desc):
                found.append(asset)
                break
    return found


def resolve_cast(description: str, assets: list[Reference], entries: list[CastEntry]) -> list[Reference]:
    """Elenco do quadro: citados na descrição + incluídos à mão − removidos à mão, com o papel de cada um."""
    by_id = {entry.asset_id: entry for entry in entries}
    detected = {asset.id for asset in mentioned_references(description, assets)}
    cast = []
    for asset in assets:
        entry = by_id.get(asset.id)
        if entry and not entry.included:
            continue
        if asset.id in detected or entry:
            cast.append(replace(asset, role=entry.role.strip() if entry else ""))
    # Personagens primeiro: são eles que mais sofrem com troca de rosto.
    return sorted(cast, key=lambda a: a.kind != 'character')


def assign_reference_files(cast: list[Reference], suffix_of, budget: int = MAX_REFERENCE_IMAGES
                           ) -> tuple[list[Reference], list[tuple[str, str]]]:
    """Escolhe quais fotos vão para a IA e dá a cada uma o nome do dono (rafa_1.png).

    Distribui o limite em rodadas (1ª foto de todos, depois a 2ª...), para nenhum personagem
    do quadro ficar sem rosto. Devolve o elenco com `files` preenchido e a lista (foto, nome).
    """
    used: set[str] = set()
    stems = []
    for asset in cast:
        stem, n = slug(asset.name), 2
        while stem in used:
            stem, n = f"{slug(asset.name)}{n}", n + 1
        used.add(stem)
        stems.append(stem)
    chosen: list[list[str]] = [[] for _ in cast]
    plan: list[tuple[str, str]] = []
    for round_ in range(PHOTOS_PER_REFERENCE):
        for i, asset in enumerate(cast):
            if len(plan) >= budget or round_ >= len(asset.photos):
                continue
            photo = asset.photos[round_]
            name = f"{stems[i]}_{round_ + 1}{suffix_of(photo)}"
            chosen[i].append(name)
            plan.append((photo, name))
    return [replace(asset, files=tuple(chosen[i])) for i, asset in enumerate(cast)], plan


def previous_context(frames: list[dict], position: int, limit: int = 30, max_chars: int = 400) -> list[str]:
    """Resumo dos cards antes deste, na ordem da HQ, para a IA saber o que já aconteceu."""
    lines = []
    for frame in frames:
        text = ' '.join(frame.get('description', '').split())
        if frame['position'] >= position or frame.get('kind') == 'credits' or not text:
            continue
        if len(text) > max_chars:
            text = text[:max_chars - 1].rstrip() + '…'
        label = 'Capa' if frame.get('kind') == 'cover' else f"Quadro {frame['position']}"
        lines.append(f"{label}: {text}")
    return lines[-limit:]


BALLOON_VERBS = {'speech': 'fala', 'thought': 'pensa', 'shout': 'grita'}


def dialogue_lines(balloons: list[dict], names: dict[str, str]) -> list[str]:
    """Texto dos balões em forma de roteiro, para a IA acertar expressões e deixar espaço."""
    lines = []
    for balloon in balloons:
        text = balloon.get('text', '').strip()
        if not text:
            continue
        if balloon.get('type') == 'caption':
            lines.append(f"Narração: {text}")
        else:
            who = names.get(balloon.get('speaker', ''), 'Alguém')
            lines.append(f"{who} ({BALLOON_VERBS.get(balloon.get('type'), 'fala')}): {text}")
    return lines


def prepare_brief(scene: str, style: str, references: list[Reference], feedback: str = "", has_previous: bool = False,
                  comic_title: str = "", comic_context: str = "", previous_file: str = "",
                  dialogue: list[str] | None = None, ai_text: bool = False, attachment_files: list[str] | None = None,
                  kind: str = 'panel', image_format: str = 'landscape', previous_frames: list[str] | None = None) -> str:
    """`ai_text`: a IA desenha balões e narração na imagem (como num chat); senão, o editor os põe por cima."""
    text_rule = ("DESENHE os balões de fala, pensamento e grito e as caixas de narração DENTRO da imagem, como numa HQ pronta. "
                 "Use exatamente as falas e narrações escritas pelo autor (o que estiver entre aspas ou depois de \"diz\", "
                 "\"fala\", \"pensa\", \"narração\"), em português do Brasil, sem erros de ortografia e sem inventar falas. "
                 "Letras de HQ legíveis, balão apontando para quem fala. Sem marcas d'água."
                 if ai_text else
                 "Não escreva balões, textos, legendas ou marcas d'água na imagem: o editor adicionará os balões depois.")
    if kind == 'cover':
        title = comic_title.strip() or 'sem título'
        lines = [
            "Crie a CAPA desta história em quadrinhos (uma ilustração de capa, não um quadro da história).",
            f"Escreva o título “{title}” em destaque, com letras de capa de HQ, sem erros de ortografia. "
            "Use só os textos que o autor pedir na descrição; não invente outros nomes nem textos.",
            "Composição de capa: personagens grandes e marcantes, clima épico, espaço para o título no alto. Sem marcas d'água.",
            f"Estilo visual da HQ: {style}",
        ]
    else:
        lines = [
            "Crie UMA imagem final em formato de quadrinho (um quadro, não uma página).",
            "Mantenha o estilo e os personagens consistentes entre quadros.",
            text_rule,
            f"Estilo visual da HQ: {style}",
        ]
    lines.append(f"Formato da imagem: {FORMATS.get(image_format, FORMATS['landscape'])}.")
    if comic_title.strip():
        lines.append(f"História em quadrinhos: {comic_title.strip()}")
    if comic_context.strip():
        lines.append("ROTEIRO E CONTEXTO DA HISTÓRIA (use para entender a cena, o tom e as relações; desenhe só o quadro descrito abaixo):")
        lines.append(comic_context.strip())
    if previous_frames:
        lines.append("CARDS ANTERIORES DA HQ (só contexto da história até aqui: NÃO desenhe estas cenas, desenhe apenas a descrição abaixo):")
        lines += [f"- {line}" for line in previous_frames]
    lines.append(f"{'Descrição da capa' if kind == 'cover' else 'Descrição do quadro'}: {scene}")
    if dialogue and ai_text:
        lines.append("TEXTO PARA OS BALÕES DESTE QUADRO (escreva exatamente assim, nesta ordem de leitura):")
        lines += [f"- {line}" for line in dialogue]
    elif dialogue:
        lines.append(f"TEXTO DESTE QUADRO (NÃO escreva na imagem: o editor coloca os balões depois. Use para acertar quem fala, "
                     f"as expressões e os gestos, e deixe área livre e pouco detalhada, de preferência no alto, para {len(dialogue)} "
                     f"{'balão' if len(dialogue) == 1 else 'balões'}):")
        lines += [f"- {line}" for line in dialogue]
    if references:
        lines.append("ELENCO DESTE QUADRO (quem é, que papel tem na cena e quais fotos mostram a aparência):")
        for asset in references:
            parts = [f"- {KIND_LABELS.get(asset.kind, asset.kind)}: {asset.name}"]
            if asset.role:
                parts.append(f"Papel neste quadro: {asset.role}")
            if asset.costume:
                parts.append(f"Figurino nesta história: {asset.costume}")
            parts.append("Fotos: " + (", ".join(asset.files) if asset.files else "nenhuma, siga a descrição"))
            if asset.traits:
                parts.append(f"Nunca pode mudar: {asset.traits}")
            if asset.avoid:
                parts.append(f"Evite: {asset.avoid}")
            parts.append(f"Aparência/contexto: {asset.description or 'não especificado'}")
            parts.append(f"Personalidade: {asset.personality or 'não especificada'}")
            lines.append(". ".join(parts) + ".")
    files = [(name, asset.name) for asset in references for name in asset.files]
    attachment_files = attachment_files or []
    if previous_file:
        files.append((previous_file, None))
    if files or attachment_files:
        lines.append("IMAGENS DE REFERÊNCIA (na pasta ./referencias/ e, quando anexadas, nesta mesma ordem):")
        lines += [f"{i}. {name} — " + (f"foto de {owner}" if owner else "versão atual deste quadro")
                  for i, (name, owner) in enumerate(files, start=1)]
        lines += [f"{i}. {name} — imagem que o autor anexou a este quadro; use como referência do jeito que a descrição "
                  f"ou os ajustes pedirem" for i, name in enumerate(attachment_files, start=len(files) + 1)]
    if any(a.kind == 'character' for a in references):
        lines.append("REGRAS DE IDENTIDADE: o rosto de cada personagem deve ser reconhecível como a pessoa das fotos com o nome "
                     "dele. Nunca use a foto de um personagem para desenhar outro, não troque rostos entre eles e não "
                     "acrescente outras pessoas reconhecíveis além do elenco acima. Figurino e pose podem mudar; o rosto, não.")
    if has_previous:
        lines.append("Há uma imagem anterior deste mesmo quadro nas referências. Use-a como base visual e preserve tudo que não foi solicitado alterar.")
    if feedback.strip():
        lines.append(f"AJUSTES PEDIDOS PELO AUTOR: {feedback.strip()}")
    lines.append("SALVE obrigatoriamente a imagem final como quadro.png, quadro.webp ou quadro.jpg NA PASTA DE TRABALHO ATUAL. Não entregue apenas uma descrição ou um link.")
    return "\n".join(lines)
