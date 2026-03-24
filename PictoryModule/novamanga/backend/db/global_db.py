import sqlite3, uuid, time
from pathlib import Path
from .schema import GLOBAL_DB_DDL

_DB_PATH = Path.home() / ".novamanga" / "global.db"


def _get_conn() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(GLOBAL_DB_DDL)
    return conn


def list_projects() -> list[dict]:
    with _get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM projects ORDER BY created_at DESC")]


def create_project(name: str, path: str) -> dict:
    with _get_conn() as conn:
        pid = str(uuid.uuid4())
        now = int(time.time() * 1000)
        conn.execute(
            "INSERT INTO projects(id,name,path,created_at,updated_at) VALUES (?,?,?,?,?)",
            (pid, name, path, now, now)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM projects WHERE id=?", [pid]).fetchone()
        return dict(row)


def get_project(project_id: str) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id=?", [project_id]).fetchone()
        return dict(row) if row else None
