"""Identificação do formato real de imagens pelos bytes do arquivo."""

from pathlib import Path


def file_type(path: Path) -> str | None:
    with path.open("rb") as stream:
        header = stream.read(16)
    if header[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if header[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return ".webp"
    return None
