"""Composição dos adaptadores concretos e casos de uso do HQ Studio."""

from dataclasses import dataclass
from pathlib import Path

from application.use_cases.generate_frame.generate_frame import ComicService
from application.use_cases.manage_studio.manage_studio import StudioService
from infra.repositories.sqlite_repository import SQLiteRepository
from infra.services.image_providers.provider_registry import ProviderRegistry
from infra.services.media_storage import LocalMediaStorage
from infra.services.pdf_exporter import build_pdf


@dataclass
class StudioContainer:
    repo: SQLiteRepository
    providers: ProviderRegistry
    media: LocalMediaStorage
    generation: ComicService
    studio: StudioService


def build_studio(base: Path) -> StudioContainer:
    media = LocalMediaStorage(base / "data" / "media")
    repo = SQLiteRepository(base / "data" / "studio.sqlite3")
    providers = ProviderRegistry(base)
    generation = ComicService(repo, providers, media)
    studio = StudioService(repo, generation, providers, media, build_pdf)
    return StudioContainer(repo, providers, media, generation, studio)
