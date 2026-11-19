"""Operações do estúdio: regras e coordenação, sem HTTP ou adaptadores concretos."""

from __future__ import annotations

from application.errors import ApplicationError, ConflictError, NotFoundError, ValidationError
from application.protocols.repository import StudioRepository
from application.protocols.services import ImageProviders, MediaStorage, PdfExporter, UploadReader
from application.use_cases.generate_frame.generate_frame import ComicService
from application.use_cases.manage_studio.protocols.requests import (
    ProjectIn,
    TextModeIn,
    ComicIn,
    FrameIn,
    AssetIn,
    CastIn,
    FrameCreateIn,
    KindIn,
    FormatIn,
    CreditsIn,
    BalloonsIn,
    CostumesIn,
    GenerationIn,
)
from domain.comics import MAX_ATTACHMENTS, MAX_PHOTOS, slug


class StudioService:
    def __init__(
        self,
        repo: StudioRepository,
        generation: ComicService,
        providers: ImageProviders,
        media: MediaStorage,
        pdf_exporter: PdfExporter,
    ):
        self.repo = repo
        self.generation = generation
        self.providers = providers
        self.media = media
        self.pdf_exporter = pdf_exporter

    @staticmethod
    def require(item, label):
        if not item:
            raise NotFoundError(f"{label} não encontrado(a).")
        return item

    def default_credits(self, comic) -> dict:
        """Créditos começam com os personagens da biblioteca: nada de nome inventado."""
        characters = [a for a in self.repo.list_assets(comic["project_id"]) if a["kind"] == "character"]
        return {
            "heading": "Elenco",
            "lines": [{"name": a["name"], "role": ""} for a in characters],
            "footer": "",
        }

    def projects_list(self):
        return self.repo.projects()

    def project_create(self, body: ProjectIn):
        return self.repo.create_project(body.name.strip(), body.style.strip())

    def project_get(self, project_id: str):
        return self.require(self.repo.project(project_id), "Projeto")

    def project_text_mode(self, project_id: str, body: TextModeIn):
        self.require(self.repo.project(project_id), "Projeto")
        return self.repo.set_text_mode(project_id, body.text_mode)

    def assets_list(self, project_id: str):
        self.require(self.repo.project(project_id), "Projeto")
        return self.repo.list_assets(project_id)

    async def assets_create(
        self,
        project_id: str,
        name: str,
        kind: str,
        description: str = "",
        personality: str = "",
        aliases: str = "",
        traits: str = "",
        avoid: str = "",
        images: list[UploadReader] | None = None,
        image: UploadReader | None = None,
    ):
        self.require(self.repo.project(project_id), "Projeto")
        if kind not in ("character", "object", "location"):
            raise ValidationError("Tipo inválido")
        if (
            not name.strip()
            or len(name) > 100
            or len(description) > 2000
            or (len(personality) > 2000)
            or (len(aliases) > 600)
            or (len(traits) > 1000)
            or (len(avoid) > 1000)
        ):
            raise ValidationError("Dados inválidos ou muito longos")
        uploads = [f for f in [image, *(images or [])] if f and f.filename]
        if len(uploads) > MAX_PHOTOS:
            raise ValidationError(f"Envie até {MAX_PHOTOS} fotos por ficha.")
        paths = []
        try:
            for upload in uploads:
                paths.append(await self.media.save(upload))
        except ApplicationError:
            for path in paths:
                self.media.remove(path)
            raise
        return self.repo.create_asset(
            project_id,
            name.strip(),
            kind,
            description.strip(),
            personality.strip(),
            aliases.strip(),
            paths,
            traits.strip(),
            avoid.strip(),
        )

    def asset_update(self, asset_id: str, body: AssetIn):
        self.require(self.repo.get_asset(asset_id), "Ficha")
        if not body.name.strip():
            raise ValidationError("O nome não pode ficar vazio.")
        return self.repo.update_asset(
            asset_id,
            body.name.strip(),
            body.description.strip(),
            body.personality.strip(),
            body.aliases.strip(),
            body.traits.strip(),
            body.avoid.strip(),
        )

    def asset_delete(self, asset_id: str):
        self.require(self.repo.get_asset(asset_id), "Ficha")
        for path in self.repo.delete_asset(asset_id):
            self.media.remove(path)

    async def asset_photo_add(
        self, asset_id: str, image: UploadReader, source: str = "upload", principal: bool = False
    ):
        asset = self.require(self.repo.get_asset(asset_id), "Ficha")
        if source not in ("upload", "frame"):
            raise ValidationError("Origem inválida")
        if len(asset["photos"]) >= MAX_PHOTOS:
            raise ValidationError(
                f"A ficha já tem {MAX_PHOTOS} fotos. Exclua alguma antes de adicionar outra."
            )
        return self.repo.add_photo(asset_id, await self.media.save(image), source, principal)

    def asset_photo_delete(self, asset_id: str, photo_id: str):
        self.require(self.repo.get_asset(asset_id), "Ficha")
        self.media.remove(self.require(self.repo.delete_photo(asset_id, photo_id), "Foto"))
        return self.repo.get_asset(asset_id)

    def asset_photo_principal(self, asset_id: str, photo_id: str):
        self.require(self.repo.get_asset(asset_id), "Ficha")
        return self.require(self.repo.set_principal_photo(asset_id, photo_id), "Foto")

    def comics_list(self, project_id: str):
        self.require(self.repo.project(project_id), "Projeto")
        return self.repo.list_comics(project_id)

    def comic_create(self, project_id: str, body: ComicIn):
        self.require(self.repo.project(project_id), "Projeto")
        style = body.style.strip() if body.style is not None and body.style.strip() else None
        return self.repo.create_comic(project_id, body.title.strip(), body.context.strip(), style)

    def comic_update(self, comic_id: str, body: ComicIn):
        self.require(self.repo.get_comic(comic_id), "HQ")
        if not body.title.strip():
            raise ValidationError("O título não pode ficar vazio.")
        style = body.style.strip() if body.style is not None and body.style.strip() else None
        return self.repo.update_comic(comic_id, body.title.strip(), body.context.strip(), style)

    def comic_delete(self, comic_id: str):
        self.require(self.repo.get_comic(comic_id), "HQ")
        if any((f["status"] in ("queued", "processing") for f in self.repo.frames(comic_id))):
            raise ConflictError("Há quadros sendo gerados nesta HQ. Espere terminar para excluir.")
        for path in self.repo.delete_comic(comic_id):
            self.media.remove(path)

    def comic_costumes(self, comic_id: str, body: CostumesIn):
        self.require(self.repo.get_comic(comic_id), "HQ")
        if any((len(v) > 600 for v in body.costumes.values())):
            raise ValidationError("Cada figurino deve ter até 600 caracteres.")
        return self.repo.set_costumes(comic_id, body.costumes)

    def frames_list(self, comic_id: str):
        self.require(self.repo.get_comic(comic_id), "HQ")
        return self.repo.frames(comic_id)

    def frames_create(self, comic_id: str, body: FrameCreateIn | None = None):
        comic = self.require(self.repo.get_comic(comic_id), "HQ")
        kind = body.kind if body else "panel"
        return self.repo.add_frame(comic_id, kind, self.default_credits(comic) if kind == "credits" else None)

    def comic_export(self, comic_id: str):
        comic = self.require(self.repo.get_comic(comic_id), "HQ")
        project = self.repo.project(comic["project_id"])
        try:
            content, skipped = self.pdf_exporter(
                comic["title"],
                self.repo.frames(comic_id),
                self.media.resolve,
                overlay_balloons=project["text_mode"] == "editor",
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return content, skipped, slug(comic["title"])

    def frame_kind(self, frame_id: str, body: KindIn):
        frame = self.require(self.repo.get_frame(frame_id), "Quadro")
        if frame["kind"] == "credits":
            raise ValidationError("A página de créditos não vira quadro nem capa.")
        return self.repo.set_kind(frame_id, body.kind)

    def frame_format(self, frame_id: str, body: FormatIn):
        self.require(self.repo.get_frame(frame_id), "Quadro")
        return self.repo.set_format(frame_id, body.format)

    def frame_credits(self, frame_id: str, body: CreditsIn):
        frame = self.require(self.repo.get_frame(frame_id), "Quadro")
        if frame["kind"] != "credits":
            raise ValidationError("Este quadro não é uma página de créditos.")
        lines = [line.model_dump() for line in body.lines if line.name.strip() or line.role.strip()]
        return self.repo.set_credits(
            frame_id, {"heading": body.heading.strip(), "lines": lines, "footer": body.footer.strip()}
        )

    def frame_update(self, frame_id: str, body: FrameIn):
        self.require(self.repo.get_frame(frame_id), "Quadro")
        return self.repo.update_description(frame_id, body.description)

    async def frame_attachment_add(self, frame_id: str, image: UploadReader):
        frame = self.require(self.repo.get_frame(frame_id), "Quadro")
        if len(frame["attachments"]) >= MAX_ATTACHMENTS:
            raise ValidationError(f"Cada quadro aceita até {MAX_ATTACHMENTS} anexos.")
        return self.repo.add_attachment(frame_id, await self.media.save(image, "attachments"))

    def frame_attachment_delete(self, frame_id: str, attachment_id: str):
        self.require(self.repo.get_frame(frame_id), "Quadro")
        self.media.remove(self.require(self.repo.delete_attachment(frame_id, attachment_id), "Anexo"))
        return self.repo.get_frame(frame_id)

    def frame_balloons(self, frame_id: str, body: BalloonsIn):
        self.require(self.repo.get_frame(frame_id), "Quadro")
        return self.repo.set_balloons(frame_id, [b.model_dump() for b in body.balloons])

    def frame_cast(self, frame_id: str, body: CastIn):
        self.require(self.repo.get_frame(frame_id), "Quadro")
        return self.repo.set_frame_cast(frame_id, [item.model_dump() for item in body.items])

    def frame_generate(self, frame_id: str, body: GenerationIn):
        try:
            return self.generation.start_generation(
                frame_id, body.provider, body.feedback, body.refine, body.model, body.effort
            )
        except LookupError as exc:
            raise NotFoundError(str(exc)) from exc
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    def versions_list(self, frame_id: str):
        self.require(self.repo.get_frame(frame_id), "Quadro")
        return self.repo.versions(frame_id)

    def version_restore(self, frame_id: str, version_id: str):
        frame = self.require(self.repo.get_frame(frame_id), "Quadro")
        if frame["status"] in ("queued", "processing"):
            raise ConflictError("Aguarde a geração terminar.")
        return self.require(self.repo.choose_version(frame_id, version_id), "Versão")

    def frame_move(self, frame_id: str, direction: str):
        frame = self.require(self.repo.get_frame(frame_id), "Quadro")
        if direction not in ("left", "right"):
            raise ValidationError("Direção inválida")
        if frame["status"] in ("queued", "processing"):
            raise ConflictError("Aguarde a geração terminar.")
        return self.repo.move_frame(frame_id, -1 if direction == "left" else 1)

    def frame_delete(self, frame_id: str):
        frame = self.require(self.repo.get_frame(frame_id), "Quadro")
        if frame["status"] in ("queued", "processing"):
            raise ConflictError("Aguarde a geração terminar.")
        self.repo.delete_frame(frame_id)

    def provider_list(self):
        return self.providers.list_public()
