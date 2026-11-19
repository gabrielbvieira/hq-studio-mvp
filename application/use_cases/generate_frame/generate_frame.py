"""Casos de uso independentes de FastAPI. Orquestra banco, arquivos e gerador."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading

from application.protocols.repository import StudioRepository
from application.protocols.services import ImageProviders, MediaStorage

from domain.comics import (
    MAX_ATTACHMENTS,
    previous_context,
    MAX_REFERENCE_IMAGES,
    CastEntry,
    Reference,
    assign_reference_files,
    dialogue_lines,
    prepare_brief,
    resolve_cast,
)


class ComicService:
    def __init__(self, repo: StudioRepository, providers: ImageProviders, media: MediaStorage):
        self.repo = repo
        self.providers = providers
        self.media = media
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="quadro")
        self.lock = threading.Lock()
        self.active: set[str] = set()

    def _media_file(self, webpath: str | None) -> Path | None:
        return self.media.resolve(webpath)

    def start_generation(
        self, frame_id: str, provider_id: str, feedback: str, refine: bool, model: str = "", effort: str = ""
    ):
        frame = self.repo.get_frame_context(frame_id)
        if not frame:
            raise LookupError("Quadro não encontrado")
        if frame["kind"] == "credits":
            raise ValueError("A página de créditos é montada pelo editor, não pela IA.")
        if not frame["description"].strip():
            raise ValueError("Descreva o quadro antes de gerar.")
        self.providers.check_options(self.providers.get(provider_id), model, effort)
        with self.lock:
            if frame_id in self.active:
                raise ValueError("Este quadro já está sendo processado.")
            self.active.add(frame_id)
            self.repo.set_job(frame_id, "queued", provider_id, feedback)
        try:
            self.executor.submit(self._worker, frame_id, provider_id, feedback, refine, model, effort)
        except Exception:
            with self.lock:
                self.active.discard(frame_id)
            raise
        return self.repo.get_frame(frame_id)

    def _worker(
        self, frame_id: str, provider_id: str, feedback: str, refine: bool, model: str = "", effort: str = ""
    ):
        try:
            self.repo.set_job(frame_id, "processing", provider_id, feedback)
            frame = self.repo.get_frame_context(frame_id)
            stored = self.repo.get_frame(frame_id)
            cast_entries = [CastEntry(c["asset_id"], c["included"], c["role"]) for c in stored["cast"]]
            costumes = self.repo.get_comic(frame["comic_id"])["costumes"]
            assets = []
            for a in self.repo.list_assets(frame["project_id"]):
                # Só fotos que existem de verdade: a IA nunca recebe um nome sem arquivo.
                photos = tuple(
                    str(path) for photo in a["photos"] if (path := self._media_file(photo["image_path"]))
                )
                assets.append(
                    Reference(
                        id=a["id"],
                        name=a["name"],
                        kind=a["kind"],
                        description=a["description"],
                        personality=a["personality"],
                        aliases=a["aliases"],
                        image_path=a["image_path"],
                        traits=a["traits"],
                        avoid=a["avoid"],
                        photos=photos,
                        costume=costumes.get(a["id"], ""),
                    )
                )
            previous = self._media_file(frame["image_path"]) if refine else None
            if previous and previous.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
                previous = None
            cast = resolve_cast(frame["description"], assets, cast_entries)
            # Anexos do autor valem mais que fotos extras da ficha: entram sempre, até o limite.
            attachments = [
                path
                for a in stored["attachments"][:MAX_ATTACHMENTS]
                if (path := self._media_file(a["image_path"]))
            ]
            budget = MAX_REFERENCE_IMAGES - (1 if previous else 0) - len(attachments)
            cast, plan = assign_reference_files(cast, lambda photo: Path(photo).suffix.lower(), budget)
            references = [(Path(photo), name) for photo, name in plan]
            previous_file = ""
            if previous:
                previous_file = "quadro_atual" + previous.suffix.lower()
                references.append((previous, previous_file))
            attachment_files = [
                f"anexo_{i}{path.suffix.lower()}" for i, path in enumerate(attachments, start=1)
            ]
            references += list(zip(attachments, attachment_files))
            prompt = prepare_brief(
                frame["description"],
                frame["style"],
                cast,
                feedback,
                bool(previous),
                frame.get("comic_title") or "",
                frame.get("comic_context") or "",
                previous_file,
                dialogue_lines(stored["balloons"], {a.id: a.name for a in assets}),
                ai_text=frame.get("text_mode", "ai") == "ai",
                attachment_files=attachment_files,
                kind=frame["kind"],
                image_format=frame["format"],
                previous_frames=previous_context(self.repo.frames(frame["comic_id"]), frame["position"]),
            )
            image_path = self.providers.generate(
                provider_id, prompt, references, frame_id, model=model, effort=effort, refine=refine
            )
            self.repo.finish_frame(frame_id, image_path, provider_id, feedback)
        except Exception as exc:
            self.repo.set_job(frame_id, "error", provider_id, feedback, str(exc)[:900])
        finally:
            with self.lock:
                self.active.discard(frame_id)
