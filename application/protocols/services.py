"""Portas de arquivos, geração de imagem e exportação."""

from pathlib import Path
from typing import Protocol


class UploadReader(Protocol):
    filename: str | None

    async def read(self, size: int = -1) -> bytes: ...


class MediaStorage(Protocol):
    def resolve(self, webpath: str | None) -> Path | None: ...
    async def save(self, image: UploadReader, folder: str = "assets") -> str: ...
    def remove(self, webpath: str | None): ...


class ImageProviders(Protocol):
    def get(self, provider_id: str) -> dict: ...
    def check_options(self, provider: dict, model: str, effort: str): ...
    def list_public(self) -> list[dict]: ...
    def generate(
        self,
        provider_id: str,
        prompt: str,
        references: list[tuple[Path, str]],
        frame_id: str,
        model: str = "",
        effort: str = "",
        refine: bool = False,
    ) -> str: ...


class PdfExporter(Protocol):
    def __call__(self, title, frames, media_file, overlay_balloons=False) -> tuple[bytes, int]: ...
