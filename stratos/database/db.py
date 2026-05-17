import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from stratos.paths import DB_PATH, ROOT

SCHEMA_PATH = ROOT / "database" / "schema.sql"


@contextmanager
def connect(db_path: Path = DB_PATH) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn, SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        conn.executescript(handle.read())


def upsert_job(job_name: str, status: str, last_run_at: str, message: str = "") -> None:
    last_success = last_run_at if status == "success" else None
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO job_runs(job_name, status, last_success_at, last_run_at, message)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(job_name) DO UPDATE SET
              status=excluded.status,
              last_success_at=COALESCE(excluded.last_success_at, job_runs.last_success_at),
              last_run_at=excluded.last_run_at,
              message=excluded.message
            """,
            (job_name, status, last_success, last_run_at, message),
        )
