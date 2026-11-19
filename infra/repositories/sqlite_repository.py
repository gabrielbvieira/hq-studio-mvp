"""Adaptador SQLite; cada operação abre sua conexão (seguro para threads)."""
from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path


def uid() -> str:
    return uuid.uuid4().hex


class SQLiteRepository:
    def __init__(self, filename: Path):
        self.filename = filename
        filename.parent.mkdir(parents=True, exist_ok=True)
        self.init()

    def db(self):
        db = sqlite3.connect(self.filename, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("PRAGMA busy_timeout = 30000")
        return db

    def init(self):
        with self.db() as db:
            db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, style TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                name TEXT NOT NULL, kind TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
                personality TEXT NOT NULL DEFAULT '', aliases TEXT NOT NULL DEFAULT '',
                image_path TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS comics (
                id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title TEXT NOT NULL, context TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS frames (
                id TEXT PRIMARY KEY, comic_id TEXT NOT NULL REFERENCES comics(id) ON DELETE CASCADE,
                position INTEGER NOT NULL, description TEXT NOT NULL DEFAULT '',
                image_path TEXT, status TEXT NOT NULL DEFAULT 'draft',
                message TEXT NOT NULL DEFAULT '', provider TEXT NOT NULL DEFAULT '',
                feedback TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS frame_versions (
                id TEXT PRIMARY KEY, frame_id TEXT NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
                image_path TEXT NOT NULL, provider TEXT NOT NULL, feedback TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS asset_photos (
                id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
                image_path TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'upload',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS comic_costumes (
                comic_id TEXT NOT NULL REFERENCES comics(id) ON DELETE CASCADE,
                asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
                costume TEXT NOT NULL, PRIMARY KEY (comic_id, asset_id)
            );
            CREATE TABLE IF NOT EXISTS frame_attachments (
                id TEXT PRIMARY KEY, frame_id TEXT NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
                image_path TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS frame_cast (
                frame_id TEXT NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
                asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
                included INTEGER NOT NULL DEFAULT 1, role TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (frame_id, asset_id)
            );
            CREATE INDEX IF NOT EXISTS idx_assets_project ON assets(project_id);
            CREATE INDEX IF NOT EXISTS idx_photos_asset ON asset_photos(asset_id);
            CREATE INDEX IF NOT EXISTS idx_comics_project ON comics(project_id);
            CREATE INDEX IF NOT EXISTS idx_frames_comic ON frames(comic_id, position);
            """)
            # Migração: bancos criados antes do roteiro da HQ.
            if 'context' not in {row[1] for row in db.execute("PRAGMA table_info(comics)")}:
                db.execute("ALTER TABLE comics ADD COLUMN context TEXT NOT NULL DEFAULT ''")
            # Migração: estilo visual por HQ; as que já existem herdam o estilo do projeto (nada muda para elas).
            if 'style' not in {row[1] for row in db.execute("PRAGMA table_info(comics)")}:
                db.execute("ALTER TABLE comics ADD COLUMN style TEXT NOT NULL DEFAULT ''")
                db.execute("UPDATE comics SET style=COALESCE((SELECT p.style FROM projects p WHERE p.id=comics.project_id), '')")
            # Migração: quem escreve o texto da HQ ('ai' desenha na imagem; 'editor' põe balões por cima).
            if 'text_mode' not in {row[1] for row in db.execute("PRAGMA table_info(projects)")}:
                db.execute("ALTER TABLE projects ADD COLUMN text_mode TEXT NOT NULL DEFAULT 'ai'")
            # Migração: tipo de página (quadro, capa, créditos), formato da imagem e texto dos créditos.
            frame_columns = {row[1] for row in db.execute("PRAGMA table_info(frames)")}
            for column, ddl in (('kind', "TEXT NOT NULL DEFAULT 'panel'"), ('format', "TEXT NOT NULL DEFAULT 'landscape'"),
                                ('credits', "TEXT NOT NULL DEFAULT '{}'")):
                if column not in frame_columns:
                    db.execute(f"ALTER TABLE frames ADD COLUMN {column} {ddl}")
            # Migração: balões e narração do quadro (lista JSON, posições em % da imagem).
            if 'balloons' not in {row[1] for row in db.execute("PRAGMA table_info(frames)")}:
                db.execute("ALTER TABLE frames ADD COLUMN balloons TEXT NOT NULL DEFAULT '[]'")
            # Migração: traços fixos e erros a evitar na ficha; foto única vira a primeira da galeria.
            asset_columns = {row[1] for row in db.execute("PRAGMA table_info(assets)")}
            for column in ('traits', 'avoid'):
                if column not in asset_columns:
                    db.execute(f"ALTER TABLE assets ADD COLUMN {column} TEXT NOT NULL DEFAULT ''")
            db.execute("""INSERT INTO asset_photos(id, asset_id, image_path)
                SELECT lower(hex(randomblob(16))), a.id, a.image_path FROM assets a WHERE a.image_path IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM asset_photos p WHERE p.asset_id=a.id AND p.image_path=a.image_path)""")
            db.execute("UPDATE frames SET status='error', message='Geração interrompida pelo reinício do servidor.' WHERE status IN ('queued','processing')")

    @staticmethod
    def one(row):
        return dict(row) if row else None

    def projects(self):
        with self.db() as db:
            return [dict(r) for r in db.execute("SELECT * FROM projects ORDER BY created_at DESC, rowid DESC")]

    def project(self, id):
        with self.db() as db:
            return self.one(db.execute("SELECT * FROM projects WHERE id=?", (id,)).fetchone())

    def set_text_mode(self, id, text_mode):
        with self.db() as db:
            db.execute("UPDATE projects SET text_mode=? WHERE id=?", (text_mode, id))
        return self.project(id)

    def create_project(self, name, style):
        id = uid()
        with self.db() as db:
            db.execute("INSERT INTO projects(id,name,style) VALUES (?,?,?)", (id, name, style))
        return self.project(id)

    @staticmethod
    def _with_photos(db, assets):
        """Anexa as fotos de cada ficha, com a principal (assets.image_path) primeiro."""
        for asset in assets:
            rows = db.execute("SELECT id,image_path,source,created_at FROM asset_photos WHERE asset_id=? "
                              "ORDER BY image_path<>?, created_at DESC, rowid DESC", (asset['id'], asset['image_path'] or ''))
            asset['photos'] = [dict(r) for r in rows]
        return assets

    def list_assets(self, project_id):
        with self.db() as db:
            assets = [dict(r) for r in db.execute("SELECT * FROM assets WHERE project_id=? ORDER BY kind, name", (project_id,))]
            return self._with_photos(db, assets)

    def get_asset(self, id):
        with self.db() as db:
            row = db.execute("SELECT * FROM assets WHERE id=?", (id,)).fetchone()
            return self._with_photos(db, [dict(row)])[0] if row else None

    def create_asset(self, project_id, name, kind, description, personality, aliases, image_paths=(), traits='', avoid=''):
        id = uid()
        with self.db() as db:
            db.execute("INSERT INTO assets(id,project_id,name,kind,description,personality,aliases,image_path,traits,avoid) VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (id, project_id, name, kind, description, personality, aliases, image_paths[0] if image_paths else None, traits, avoid))
            for path in image_paths:
                db.execute("INSERT INTO asset_photos(id,asset_id,image_path) VALUES (?,?,?)", (uid(), id, path))
        return self.get_asset(id)

    def update_asset(self, id, name, description, personality, aliases, traits, avoid):
        with self.db() as db:
            db.execute("UPDATE assets SET name=?,description=?,personality=?,aliases=?,traits=?,avoid=? WHERE id=?",
                       (name, description, personality, aliases, traits, avoid, id))
        return self.get_asset(id)

    def delete_asset(self, id):
        """Exclui a ficha e devolve as fotos que ficaram sem uso, para o chamador apagar os arquivos."""
        with self.db() as db:
            paths = [r[0] for r in db.execute("SELECT image_path FROM asset_photos WHERE asset_id=?", (id,))]
            db.execute("DELETE FROM assets WHERE id=?", (id,))
        return paths

    def add_photo(self, asset_id, image_path, source='upload', principal=False):
        with self.db() as db:
            db.execute("INSERT INTO asset_photos(id,asset_id,image_path,source) VALUES (?,?,?,?)", (uid(), asset_id, image_path, source))
            db.execute("UPDATE assets SET image_path=? WHERE id=? AND (image_path IS NULL OR ?)", (image_path, asset_id, principal))
        return self.get_asset(asset_id)

    def delete_photo(self, asset_id, photo_id):
        with self.db() as db:
            row = db.execute("SELECT image_path FROM asset_photos WHERE id=? AND asset_id=?", (photo_id, asset_id)).fetchone()
            if not row:
                return None
            db.execute("DELETE FROM asset_photos WHERE id=?", (photo_id,))
            # Se era a principal, a mais recente que sobrou assume.
            db.execute("""UPDATE assets SET image_path=(SELECT image_path FROM asset_photos WHERE asset_id=?
                          ORDER BY created_at DESC, rowid DESC LIMIT 1) WHERE id=? AND image_path=?""",
                       (asset_id, asset_id, row['image_path']))
        return row['image_path']

    def set_principal_photo(self, asset_id, photo_id):
        with self.db() as db:
            row = db.execute("SELECT image_path FROM asset_photos WHERE id=? AND asset_id=?", (photo_id, asset_id)).fetchone()
            if not row:
                return None
            db.execute("UPDATE assets SET image_path=? WHERE id=?", (row['image_path'], asset_id))
        return self.get_asset(asset_id)

    @staticmethod
    def _with_costumes(db, comics):
        for comic in comics:
            comic['costumes'] = {r['asset_id']: r['costume'] for r in
                                 db.execute("SELECT asset_id,costume FROM comic_costumes WHERE comic_id=?", (comic['id'],))}
        return comics

    def list_comics(self, project_id):
        with self.db() as db:
            comics = [dict(r) for r in db.execute("SELECT * FROM comics WHERE project_id=? ORDER BY created_at DESC, rowid DESC", (project_id,))]
            return self._with_costumes(db, comics)

    def get_comic(self, id):
        with self.db() as db:
            row = db.execute("SELECT * FROM comics WHERE id=?", (id,)).fetchone()
            return self._with_costumes(db, [dict(row)])[0] if row else None

    def set_costumes(self, comic_id, costumes: dict[str, str]):
        """Troca todos os figurinos da HQ; ignora fichas de outro projeto."""
        with self.db() as db:
            db.execute("DELETE FROM comic_costumes WHERE comic_id=?", (comic_id,))
            for asset_id, costume in costumes.items():
                if costume.strip():
                    db.execute("""INSERT INTO comic_costumes(comic_id,asset_id,costume)
                                  SELECT c.id, a.id, ? FROM comics c JOIN assets a ON a.project_id=c.project_id
                                  WHERE c.id=? AND a.id=?""", (costume.strip(), comic_id, asset_id))
        return self.get_comic(comic_id)

    def create_comic(self, project_id, title, context='', style=None):
        """Sem estilo informado, a HQ nasce com o estilo padrão do projeto."""
        id = uid()
        with self.db() as db:
            db.execute("""INSERT INTO comics(id, project_id, title, context, style)
                          SELECT ?, ?, ?, ?, COALESCE(?, p.style) FROM projects p WHERE p.id=?""",
                       (id, project_id, title, context, style, project_id))
        return self.get_comic(id)

    def update_comic(self, id, title, context, style=None):
        with self.db() as db:
            db.execute("UPDATE comics SET title=?, context=?, style=COALESCE(?, style) WHERE id=?", (title, context, style, id))
        return self.get_comic(id)

    @staticmethod
    def _with_cast(db, frames):
        for frame in frames:
            frame['balloons'] = json.loads(frame.get('balloons') or '[]')
            frame['credits'] = json.loads(frame.get('credits') or '{}')
            frame['attachments'] = [dict(r) for r in db.execute(
                "SELECT id,image_path FROM frame_attachments WHERE frame_id=? ORDER BY created_at, rowid", (frame['id'],))]
            frame['cast'] = [{'asset_id': r['asset_id'], 'included': bool(r['included']), 'role': r['role']} for r in
                             db.execute("SELECT asset_id,included,role FROM frame_cast WHERE frame_id=?", (frame['id'],))]
        return frames

    def frames(self, comic_id):
        with self.db() as db:
            frames = [dict(r) for r in db.execute("SELECT * FROM frames WHERE comic_id=? ORDER BY position, rowid", (comic_id,))]
            return self._with_cast(db, frames)

    def get_frame(self, id):
        with self.db() as db:
            row = db.execute("SELECT * FROM frames WHERE id=?", (id,)).fetchone()
            return self._with_cast(db, [dict(row)])[0] if row else None

    def add_attachment(self, frame_id, image_path):
        with self.db() as db:
            db.execute("INSERT INTO frame_attachments(id,frame_id,image_path) VALUES (?,?,?)", (uid(), frame_id, image_path))
        return self.get_frame(frame_id)

    def delete_attachment(self, frame_id, attachment_id):
        with self.db() as db:
            row = db.execute("SELECT image_path FROM frame_attachments WHERE id=? AND frame_id=?", (attachment_id, frame_id)).fetchone()
            if row:
                db.execute("DELETE FROM frame_attachments WHERE id=?", (attachment_id,))
        return row['image_path'] if row else None

    def set_balloons(self, frame_id, balloons: list[dict]):
        with self.db() as db:
            db.execute("UPDATE frames SET balloons=? WHERE id=?", (json.dumps(balloons, ensure_ascii=False), frame_id))
        return self.get_frame(frame_id)

    def set_frame_cast(self, frame_id, entries: list[dict]):
        """Troca os ajustes de elenco do quadro; ignora fichas de outro projeto."""
        with self.db() as db:
            db.execute("DELETE FROM frame_cast WHERE frame_id=?", (frame_id,))
            for entry in entries:
                db.execute("""INSERT OR REPLACE INTO frame_cast(frame_id,asset_id,included,role)
                              SELECT f.id, a.id, ?, ? FROM frames f JOIN comics c ON c.id=f.comic_id
                              JOIN assets a ON a.project_id=c.project_id WHERE f.id=? AND a.id=?""",
                           (int(entry['included']), entry['role'].strip(), frame_id, entry['asset_id']))
        return self.get_frame(frame_id)

    def add_frame(self, comic_id, kind='panel', credits=None):
        """A capa entra no começo da HQ; quadros e créditos, no fim."""
        id = uid()
        image_format = 'landscape' if kind == 'panel' else 'portrait'
        with self.db() as db:
            if kind == 'cover':
                db.execute("UPDATE frames SET position=position+1 WHERE comic_id=?", (comic_id,))
                position = 1
            else:
                position = db.execute("SELECT COALESCE(MAX(position),0)+1 FROM frames WHERE comic_id=?", (comic_id,)).fetchone()[0]
            db.execute("INSERT INTO frames(id, comic_id, position, kind, format, credits) VALUES (?,?,?,?,?,?)",
                       (id, comic_id, position, kind, image_format, json.dumps(credits or {}, ensure_ascii=False)))
        return self.get_frame(id)

    def set_kind(self, id, kind):
        """Quadro ↔ capa: a capa nasce em retrato, o quadro em paisagem (o autor pode trocar depois)."""
        with self.db() as db:
            db.execute("UPDATE frames SET kind=?, format=? WHERE id=? AND kind<>'credits'",
                       (kind, 'portrait' if kind == 'cover' else 'landscape', id))
        return self.get_frame(id)

    def set_format(self, id, image_format):
        with self.db() as db:
            db.execute("UPDATE frames SET format=? WHERE id=?", (image_format, id))
        return self.get_frame(id)

    def set_credits(self, id, credits: dict):
        with self.db() as db:
            db.execute("UPDATE frames SET credits=? WHERE id=?", (json.dumps(credits, ensure_ascii=False), id))
        return self.get_frame(id)

    def update_description(self, id, description):
        with self.db() as db:
            db.execute("UPDATE frames SET description=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (description, id))
        return self.get_frame(id)

    def set_job(self, id, status, provider, feedback='', message=''):
        with self.db() as db:
            db.execute("UPDATE frames SET status=?,provider=?,feedback=?,message=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                       (status, provider, feedback, message, id))

    def finish_frame(self, id, image_path, provider, feedback):
        with self.db() as db:
            db.execute("INSERT INTO frame_versions(id,frame_id,image_path,provider,feedback) VALUES (?,?,?,?,?)",
                       (uid(), id, image_path, provider, feedback))
            db.execute("UPDATE frames SET status='done',image_path=?,message='',updated_at=CURRENT_TIMESTAMP WHERE id=?", (image_path, id))

    def versions(self, frame_id):
        with self.db() as db:
            return [dict(r) for r in db.execute("SELECT * FROM frame_versions WHERE frame_id=? ORDER BY created_at DESC, rowid DESC", (frame_id,))]

    def choose_version(self, frame_id, version_id):
        with self.db() as db:
            row = db.execute("SELECT image_path FROM frame_versions WHERE id=? AND frame_id=?", (version_id, frame_id)).fetchone()
            if not row:
                return None
            db.execute("UPDATE frames SET image_path=?,status='done',message='',updated_at=CURRENT_TIMESTAMP WHERE id=?", (row['image_path'], frame_id))
        return self.get_frame(frame_id)

    def get_frame_context(self, frame_id):
        with self.db() as db:
            return self.one(db.execute("""
                SELECT f.*, c.title comic_title, c.context comic_context, c.project_id, COALESCE(NULLIF(TRIM(c.style), ''), p.style) style, p.text_mode
                FROM frames f JOIN comics c ON f.comic_id=c.id
                JOIN projects p ON p.id=c.project_id WHERE f.id=?
            """, (frame_id,)).fetchone())

    def delete_comic(self, id):
        """Exclui a HQ (quadros, versões, anexos, balões) e devolve as imagens dela, para apagar do disco."""
        with self.db() as db:
            paths = {r[0] for r in db.execute("""
                SELECT f.image_path FROM frames f WHERE f.comic_id=? AND f.image_path IS NOT NULL
                UNION SELECT v.image_path FROM frame_versions v JOIN frames f ON f.id=v.frame_id WHERE f.comic_id=?
                UNION SELECT a.image_path FROM frame_attachments a JOIN frames f ON f.id=a.frame_id WHERE f.comic_id=?""",
                (id, id, id))}
            db.execute("DELETE FROM comics WHERE id=?", (id,))
        return sorted(paths)

    def delete_frame(self, id):
        with self.db() as db:
            frame = db.execute("SELECT comic_id,position FROM frames WHERE id=?", (id,)).fetchone()
            if not frame:
                return
            db.execute("DELETE FROM frames WHERE id=?", (id,))
            db.execute("UPDATE frames SET position=position-1 WHERE comic_id=? AND position>?",
                       (frame['comic_id'], frame['position']))

    def move_frame(self, id, direction):
        frame = self.get_frame(id)
        if not frame:
            return None
        frames = self.frames(frame['comic_id'])
        pos = next(i for i, f in enumerate(frames) if f['id'] == id)
        other = pos + direction
        if not 0 <= other < len(frames):
            return frame
        a, b = frames[pos], frames[other]
        with self.db() as db:
            db.execute("UPDATE frames SET position=? WHERE id=?", (b['position'], a['id']))
            db.execute("UPDATE frames SET position=? WHERE id=?", (a['position'], b['id']))
        return self.get_frame(id)
