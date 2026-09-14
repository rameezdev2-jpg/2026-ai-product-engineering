"""Small shared infrastructure, copied into each independently runnable project."""
import json
from contextlib import contextmanager
import os
import secrets
import sqlite3
from pathlib import Path
from fastapi import Header, HTTPException

def identity(authorization: str = Header(default="")) -> str:
    # Tokens map to tenants on the server; the caller cannot choose a tenant header.
    keys = json.loads(os.getenv("API_KEYS_JSON", '{"local-demo-key":"demo"}'))
    token = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
    for key, tenant in keys.items():
        if token and secrets.compare_digest(token, key):
            return tenant
    raise HTTPException(401, "Valid bearer token required")

@contextmanager
def db():
    path = Path(os.getenv("DATABASE_PATH", "data/app.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()

def save(tenant, kind, payload):
    with db() as conn:
        cur = conn.execute("INSERT INTO records(tenant,kind,payload) VALUES(?,?,?)", (tenant, kind, json.dumps(payload)))
        return cur.lastrowid

def records(tenant, kind):
    with db() as conn:
        return [dict(id=r['id'], **json.loads(r['payload'])) for r in conn.execute("SELECT * FROM records WHERE tenant=? AND kind=? ORDER BY id", (tenant, kind))]
