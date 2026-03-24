import sqlite3, uuid, time, json
from pathlib import Path
from .schema import PROJECT_DB_DDL


def get_conn(project_path: str) -> sqlite3.Connection:
    db_path = Path(project_path) / "project.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(PROJECT_DB_DDL)
    return conn


def create_chapter(project_path: str, project_id: str, title: str, order_index: int) -> dict:
    with get_conn(project_path) as conn:
        cid = str(uuid.uuid4())
        now = int(time.time() * 1000)
        conn.execute(
            "INSERT INTO chapters(id,project_id,title,order_index,raw_text,parse_status,created_at,updated_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (cid, project_id, title, order_index, '', 'idle', now, now)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM chapters WHERE id=?", [cid]).fetchone()
        return dict(row)


def get_chapter(project_path: str, chapter_id: str) -> dict | None:
    with get_conn(project_path) as conn:
        row = conn.execute("SELECT * FROM chapters WHERE id=?", [chapter_id]).fetchone()
        return dict(row) if row else None


def update_chapter(project_path: str, chapter_id: str, **kwargs) -> dict:
    allowed = {"title", "raw_text", "order_index", "parse_status"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    fields["updated_at"] = int(time.time() * 1000)
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [chapter_id]
    with get_conn(project_path) as conn:
        conn.execute(f"UPDATE chapters SET {sets} WHERE id=?", vals)
    return get_chapter(project_path, chapter_id)


def list_chapters(project_path: str) -> list[dict]:
    with get_conn(project_path) as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM chapters ORDER BY order_index"
        )]


def create_zone(project_path: str, chapter_id: str, data: dict) -> dict:
    with get_conn(project_path) as conn:
        zid = str(uuid.uuid4())
        now = int(time.time() * 1000)
        conn.execute(
            "INSERT INTO zones(id,chapter_id,order_index,text_content,"
            "start_char_index,end_char_index,scene_id,emotion_primary,"
            "emotion_intensity,characters_present,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                zid, chapter_id,
                data.get("order_index", 0),
                data["text_content"],
                data.get("start_char_index", 0),
                data.get("end_char_index", 0),
                data.get("scene_id"),
                data.get("emotion_primary", "平静"),
                data.get("emotion_intensity", 0.5),
                json.dumps(data.get("characters_present", []), ensure_ascii=False),
                now,
            )
        )
        conn.commit()
        row = conn.execute("SELECT * FROM zones WHERE id=?", [zid]).fetchone()
        return dict(row)


def get_zone(project_path: str, zone_id: str) -> dict | None:
    with get_conn(project_path) as conn:
        row = conn.execute("SELECT * FROM zones WHERE id=?", [zone_id]).fetchone()
        return dict(row) if row else None


def list_zones(project_path: str, chapter_id: str) -> list[dict]:
    with get_conn(project_path) as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM zones WHERE chapter_id=? ORDER BY order_index", [chapter_id]
        )]


def update_zone(project_path: str, zone_id: str, **kwargs) -> dict:
    allowed = {"order_index", "text_content", "emotion_primary",
               "emotion_intensity", "audio_asset_id", "image_asset_id",
               "duration_ms", "prompt_positive", "prompt_negative"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return get_zone(project_path, zone_id)
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [zone_id]
    with get_conn(project_path) as conn:
        conn.execute(f"UPDATE zones SET {sets} WHERE id=?", vals)
    return get_zone(project_path, zone_id)


def enqueue_task(project_path: str, task_type: str, payload: dict,
                 reference_id: str, reference_type: str, max_retries: int = 3) -> dict:
    with get_conn(project_path) as conn:
        tid = str(uuid.uuid4())
        now = int(time.time() * 1000)
        conn.execute(
            "INSERT INTO tasks(id,type,payload,status,retry_count,max_retries,"
            "reference_id,reference_type,created_at,updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (tid, task_type, json.dumps(payload), 'pending', 0, max_retries,
             reference_id, reference_type, now, now)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM tasks WHERE id=?", [tid]).fetchone()
        return dict(row)


def get_task(project_path: str, task_id: str) -> dict | None:
    with get_conn(project_path) as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", [task_id]).fetchone()
        return dict(row) if row else None


def fetch_pending_tasks(project_path: str, limit: int = 10) -> list[dict]:
    with get_conn(project_path) as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE status='pending' ORDER BY created_at LIMIT ?",
            [limit]
        ).fetchall()
        return [dict(r) for r in rows]


def update_task(project_path: str, task_id: str, **kwargs) -> dict:
    allowed = {"status", "retry_count", "error_message", "result"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    fields["updated_at"] = int(time.time() * 1000)
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [task_id]
    with get_conn(project_path) as conn:
        conn.execute(f"UPDATE tasks SET {sets} WHERE id=?", vals)
    return get_task(project_path, task_id)


def create_character(project_path: str, project_id: str, name: str, raw_description: str = "") -> dict:
    with get_conn(project_path) as conn:
        cid = str(uuid.uuid4())
        now = int(time.time() * 1000)
        conn.execute(
            "INSERT INTO characters(id,project_id,name,raw_description,created_at) VALUES (?,?,?,?,?)",
            (cid, project_id, name, raw_description, now)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM characters WHERE id=?", [cid]).fetchone()
        return dict(row)


def list_characters(project_path: str, project_id: str) -> list[dict]:
    with get_conn(project_path) as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM characters WHERE project_id=?", [project_id]
        )]


def list_all_characters(project_path: str) -> list[dict]:
    with get_conn(project_path) as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM characters")]


def get_character(project_path: str, character_id: str) -> dict | None:
    with get_conn(project_path) as conn:
        row = conn.execute("SELECT * FROM characters WHERE id=?", [character_id]).fetchone()
        return dict(row) if row else None


def list_character_variants(project_path: str, character_id: str) -> list[dict]:
    with get_conn(project_path) as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM character_variants WHERE character_id=?", [character_id]
        )]
