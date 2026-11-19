"""Armazenamento local de referências, anexos e quadros."""

import tempfile
import uuid
from pathlib import Path

from application.errors import ValidationError
from application.protocols.services import UploadReader
from infra.services.image_files import file_type


class LocalMediaStorage:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, webpath: str | None) -> Path | None:
        if not webpath or not webpath.startswith("/media/"):
            return None
        local = (self.root / webpath.removeprefix("/media/")).resolve()
        if local == self.root or self.root not in local.parents:
            return None
        return local if local.is_file() else None

    async def save(self, image: UploadReader, folder: str = "assets") -> str:
        with tempfile.NamedTemporaryFile(delete=False, dir=self.root) as stream:
            temp = Path(stream.name)
            try:
                while chunk := await image.read(1024 * 1024):
                    stream.write(chunk)
            except BaseException:
                temp.unlink(missing_ok=True)
                raise
        try:
            suffix = file_type(temp)
            if suffix is None:
                raise ValidationError("Envie PNG, JPG ou WebP")
            (self.root / folder).mkdir(exist_ok=True)
            dest = self.root / folder / (uuid.uuid4().hex + suffix)
            temp.replace(dest)
            return f"/media/{folder}/{dest.name}"
        finally:
            temp.unlink(missing_ok=True)

    def remove(self, webpath: str | None):
        local = self.resolve(webpath)
        if local:
            local.unlink(missing_ok=True)
