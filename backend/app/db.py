"""Neon Postgres connection and schema setup for ContextMap."""
import os
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "db" / "schema.sql"


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
    return url


@contextmanager
def get_conn():
    with psycopg.connect(database_url(), row_factory=dict_row) as conn:
        yield conn


def init_schema() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.execute(sql)
        conn.commit()
