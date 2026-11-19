"""Adaptadores HTTP: validação das entradas e serialização das respostas."""

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import Response

from application.use_cases.manage_studio.manage_studio import StudioService
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


def create_studio_router(studio: StudioService) -> APIRouter:
    router = APIRouter()

    @router.get("/api/projects")
    def projects_list():
        return studio.projects_list()

    @router.post("/api/projects", status_code=201)
    def project_create(body: ProjectIn):
        return studio.project_create(body)

    @router.get("/api/projects/{project_id}")
    def project_get(project_id: str):
        return studio.project_get(project_id)

    @router.patch("/api/projects/{project_id}/text-mode")
    def project_text_mode(project_id: str, body: TextModeIn):
        return studio.project_text_mode(project_id, body)

    @router.get("/api/projects/{project_id}/assets")
    def assets_list(project_id: str):
        return studio.assets_list(project_id)

    @router.post("/api/projects/{project_id}/assets", status_code=201)
    async def assets_create(
        project_id: str,
        name: str = Form(...),
        kind: str = Form(...),
        description: str = Form(""),
        personality: str = Form(""),
        aliases: str = Form(""),
        traits: str = Form(""),
        avoid: str = Form(""),
        images: list[UploadFile] | None = File(None),
        image: UploadFile | None = File(None),
    ):
        return await studio.assets_create(
            project_id, name, kind, description, personality, aliases, traits, avoid, images, image
        )

    @router.patch("/api/assets/{asset_id}")
    def asset_update(asset_id: str, body: AssetIn):
        return studio.asset_update(asset_id, body)

    @router.delete("/api/assets/{asset_id}", status_code=204)
    def asset_delete(asset_id: str):
        return studio.asset_delete(asset_id)

    @router.post("/api/assets/{asset_id}/photos", status_code=201)
    async def asset_photo_add(
        asset_id: str,
        image: UploadFile = File(...),
        source: str = Form("upload"),
        principal: bool = Form(False),
    ):
        return await studio.asset_photo_add(asset_id, image, source, principal)

    @router.delete("/api/assets/{asset_id}/photos/{photo_id}")
    def asset_photo_delete(asset_id: str, photo_id: str):
        return studio.asset_photo_delete(asset_id, photo_id)

    @router.post("/api/assets/{asset_id}/photos/{photo_id}/principal")
    def asset_photo_principal(asset_id: str, photo_id: str):
        return studio.asset_photo_principal(asset_id, photo_id)

    @router.get("/api/projects/{project_id}/comics")
    def comics_list(project_id: str):
        return studio.comics_list(project_id)

    @router.post("/api/projects/{project_id}/comics", status_code=201)
    def comic_create(project_id: str, body: ComicIn):
        return studio.comic_create(project_id, body)

    @router.patch("/api/comics/{comic_id}")
    def comic_update(comic_id: str, body: ComicIn):
        return studio.comic_update(comic_id, body)

    @router.delete("/api/comics/{comic_id}", status_code=204)
    def comic_delete(comic_id: str):
        return studio.comic_delete(comic_id)

    @router.put("/api/comics/{comic_id}/costumes")
    def comic_costumes(comic_id: str, body: CostumesIn):
        return studio.comic_costumes(comic_id, body)

    @router.get("/api/comics/{comic_id}/frames")
    def frames_list(comic_id: str):
        return studio.frames_list(comic_id)

    @router.post("/api/comics/{comic_id}/frames", status_code=201)
    def frames_create(comic_id: str, body: FrameCreateIn | None = None):
        return studio.frames_create(comic_id, body)

    @router.get("/api/comics/{comic_id}/export.pdf")
    def comic_export(comic_id: str):
        content, skipped, filename = studio.comic_export(comic_id)
        return Response(
            content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.pdf"',
                "X-Skipped-Frames": str(skipped),
            },
        )

    @router.patch("/api/frames/{frame_id}/kind")
    def frame_kind(frame_id: str, body: KindIn):
        return studio.frame_kind(frame_id, body)

    @router.patch("/api/frames/{frame_id}/format")
    def frame_format(frame_id: str, body: FormatIn):
        return studio.frame_format(frame_id, body)

    @router.put("/api/frames/{frame_id}/credits")
    def frame_credits(frame_id: str, body: CreditsIn):
        return studio.frame_credits(frame_id, body)

    @router.patch("/api/frames/{frame_id}")
    def frame_update(frame_id: str, body: FrameIn):
        return studio.frame_update(frame_id, body)

    @router.post("/api/frames/{frame_id}/attachments", status_code=201)
    async def frame_attachment_add(frame_id: str, image: UploadFile = File(...)):
        return await studio.frame_attachment_add(frame_id, image)

    @router.delete("/api/frames/{frame_id}/attachments/{attachment_id}")
    def frame_attachment_delete(frame_id: str, attachment_id: str):
        return studio.frame_attachment_delete(frame_id, attachment_id)

    @router.put("/api/frames/{frame_id}/balloons")
    def frame_balloons(frame_id: str, body: BalloonsIn):
        return studio.frame_balloons(frame_id, body)

    @router.put("/api/frames/{frame_id}/cast")
    def frame_cast(frame_id: str, body: CastIn):
        return studio.frame_cast(frame_id, body)

    @router.post("/api/frames/{frame_id}/generate", status_code=202)
    def frame_generate(frame_id: str, body: GenerationIn):
        return studio.frame_generate(frame_id, body)

    @router.get("/api/frames/{frame_id}/versions")
    def versions_list(frame_id: str):
        return studio.versions_list(frame_id)

    @router.post("/api/frames/{frame_id}/versions/{version_id}/restore")
    def version_restore(frame_id: str, version_id: str):
        return studio.version_restore(frame_id, version_id)

    @router.post("/api/frames/{frame_id}/move/{direction}")
    def frame_move(frame_id: str, direction: str):
        return studio.frame_move(frame_id, direction)

    @router.delete("/api/frames/{frame_id}", status_code=204)
    def frame_delete(frame_id: str):
        return studio.frame_delete(frame_id)

    @router.get("/api/providers")
    def provider_list():
        return studio.provider_list()

    return router
