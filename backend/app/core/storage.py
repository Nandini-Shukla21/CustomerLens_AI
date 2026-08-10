from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from app.config import settings


def _database_path() -> Path:
    path = Path(getattr(settings, "sqlite_path", "./customerlens.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_database_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def initialize_database() -> None:
    with connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'Viewer', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS datasets (id TEXT PRIMARY KEY, filename TEXT NOT NULL, path TEXT NOT NULL, rows INTEGER NOT NULL, columns INTEGER NOT NULL, schema_json TEXT NOT NULL, summary_json TEXT NOT NULL, owner_id INTEGER, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(owner_id) REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, filename TEXT NOT NULL, path TEXT NOT NULL, content TEXT NOT NULL, chunks_json TEXT NOT NULL, checksum TEXT, indexed_at TEXT, owner_id INTEGER, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(owner_id) REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS customers (id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL, payload_json TEXT NOT NULL, name TEXT, email TEXT, phone TEXT, revenue REAL DEFAULT 0, transactions REAL DEFAULT 0, ltv REAL DEFAULT 0, risk REAL DEFAULT 0, churn REAL DEFAULT 0, FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS predictions (id TEXT PRIMARY KEY, customer_id TEXT, dataset_id TEXT, prediction TEXT NOT NULL, probability REAL NOT NULL, confidence REAL NOT NULL, explanation_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS chat_history (id TEXT PRIMARY KEY, user_id INTEGER, question TEXT NOT NULL, answer TEXT NOT NULL, sources_json TEXT NOT NULL, confidence REAL NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS insights (id TEXT PRIMARY KEY, dataset_id TEXT, title TEXT NOT NULL, description TEXT NOT NULL, priority TEXT NOT NULL, confidence REAL NOT NULL, action TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS activity_log (
    id TEXT PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT,
    entity_name TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
        CREATE TABLE IF NOT EXISTS uploads (id TEXT PRIMARY KEY, dataset_id TEXT, document_id TEXT, owner_id INTEGER, filename TEXT NOT NULL, file_type TEXT, size_bytes INTEGER DEFAULT 0, status TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(owner_id) REFERENCES users(id));
        """)
        # SQLite cannot add a NOT NULL column without a value to an existing table.
        # Add it safely, backfill a useful value, then all application writes include it.
        user_columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)")}
        if "name" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN name TEXT")
            conn.execute("UPDATE users SET name = substr(email, 1, instr(email, '@') - 1) WHERE name IS NULL OR trim(name) = ''")
        for table, column, declaration in (
            ("documents", "checksum", "TEXT"), ("documents", "indexed_at", "TEXT"), ("documents", "file_type", "TEXT"), ("documents", "size_bytes", "INTEGER DEFAULT 0"),
            ("uploads", "owner_id", "INTEGER"), ("uploads", "file_type", "TEXT"),
            ("uploads", "size_bytes", "INTEGER DEFAULT 0"),
        ):
            columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
            if column not in columns:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")


def row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def decode_json(value: str | None, fallback: Any) -> Any:
    try:
        return json.loads(value or "")
    except json.JSONDecodeError:
        return fallback
