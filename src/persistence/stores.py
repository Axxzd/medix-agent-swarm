from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from src.contracts.tasks import EndReason, TaskRecord, TaskStatus


class SqliteRuntimeStore:
    def __init__(self, *, db_path: str | Path, encryption_key: str) -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._encryption_key = encryption_key.encode("utf-8")
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                parent_task_id TEXT,
                thread_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                graph_name TEXT NOT NULL,
                graph_version TEXT NOT NULL,
                status TEXT NOT NULL,
                end_reason TEXT,
                payload_encrypted TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS task_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS review_tickets (
                ticket_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                reason TEXT NOT NULL,
                reviewer_id TEXT,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                graph_version TEXT NOT NULL,
                state_blob TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS threads (
                thread_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    def list_tables(self) -> set[str]:
        rows = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table';"
        ).fetchall()
        return {str(row["name"]) for row in rows}

    def create_task(self, task: TaskRecord, payload: dict[str, Any]) -> None:
        payload_encrypted = self._encrypt_json(payload)
        self._conn.execute(
            """
            INSERT INTO tasks (
                task_id, parent_task_id, thread_id, user_id,
                graph_name, graph_version, status, end_reason,
                payload_encrypted, payload_hash, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.task_id,
                task.parent_task_id,
                task.thread_id,
                task.user_id,
                task.graph_name,
                task.graph_version,
                task.status.value,
                task.end_reason.value if task.end_reason else None,
                payload_encrypted,
                task.payload_hash,
                task.created_at.isoformat(),
                task.updated_at.isoformat(),
            ),
        )
        self._conn.commit()

    def fetch_task(self, task_id: str) -> TaskRecord | None:
        row = self._conn.execute(
            """
            SELECT task_id, parent_task_id, thread_id, user_id,
                   graph_name, graph_version, status, end_reason,
                   payload_encrypted, payload_hash, created_at, updated_at
            FROM tasks WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        if row is None:
            return None

        payload = self._decrypt_json(str(row["payload_encrypted"]))
        end_reason_raw = row["end_reason"]
        end_reason = EndReason(end_reason_raw) if end_reason_raw else None

        return TaskRecord(
            task_id=str(row["task_id"]),
            parent_task_id=str(row["parent_task_id"]) if row["parent_task_id"] else None,
            thread_id=str(row["thread_id"]),
            user_id=str(row["user_id"]),
            graph_name=str(row["graph_name"]),
            graph_version=str(row["graph_version"]),
            status=TaskStatus(str(row["status"])),
            end_reason=end_reason,
            payload=payload,
            payload_hash=str(row["payload_hash"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
        )

    def raw_payload_blob(self, task_id: str) -> str | None:
        row = self._conn.execute(
            "SELECT payload_encrypted FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return None
        return str(row["payload_encrypted"])

    def save_checkpoint(
        self,
        *,
        task_id: str,
        thread_id: str,
        graph_version: str,
        state: dict[str, Any],
    ) -> int:
        state_blob = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        cursor = self._conn.execute(
            """
            INSERT INTO checkpoints (task_id, thread_id, graph_version, state_blob, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (task_id, thread_id, graph_version, state_blob, datetime.utcnow().isoformat()),
        )
        self._conn.commit()
        return int(cursor.lastrowid)

    def load_latest_checkpoint(
        self, task_id: str, thread_id: str
    ) -> dict[str, Any] | None:
        row = self._conn.execute(
            """
            SELECT checkpoint_id, task_id, thread_id, graph_version, state_blob, created_at
            FROM checkpoints
            WHERE task_id = ? AND thread_id = ?
            ORDER BY checkpoint_id DESC
            LIMIT 1
            """,
            (task_id, thread_id),
        ).fetchone()
        if row is None:
            return None

        return {
            "checkpoint_id": int(row["checkpoint_id"]),
            "task_id": str(row["task_id"]),
            "thread_id": str(row["thread_id"]),
            "graph_version": str(row["graph_version"]),
            "state": json.loads(str(row["state_blob"])),
            "created_at": str(row["created_at"]),
        }

    def append_task_event(
        self,
        *,
        task_id: str,
        thread_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO task_events (task_id, thread_id, event_type, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                task_id,
                thread_id,
                event_type,
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                datetime.utcnow().isoformat(),
            ),
        )
        self._conn.commit()

    def append_audit_event(
        self,
        *,
        task_id: str,
        thread_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO audit_events (task_id, thread_id, event_type, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                task_id,
                thread_id,
                event_type,
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                datetime.utcnow().isoformat(),
            ),
        )
        self._conn.commit()

    def upsert_thread(self, *, thread_id: str, user_id: str) -> None:
        self._conn.execute(
            """
            INSERT INTO threads (thread_id, user_id, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(thread_id) DO NOTHING
            """,
            (thread_id, user_id, datetime.utcnow().isoformat()),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def redact_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        redacted = dict(payload)
        for key in ("patient_name", "name", "phone", "email", "id_number"):
            if key in redacted:
                redacted[key] = "[REDACTED]"
        return redacted

    def _encrypt_json(self, payload: dict[str, Any]) -> str:
        plaintext = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        key = hashlib.sha256(self._encryption_key).digest()
        cipher = bytes(byte ^ key[index % len(key)] for index, byte in enumerate(plaintext))
        return base64.urlsafe_b64encode(cipher).decode("ascii")

    def _decrypt_json(self, encrypted: str) -> dict[str, Any]:
        cipher = base64.urlsafe_b64decode(encrypted.encode("ascii"))
        key = hashlib.sha256(self._encryption_key).digest()
        plaintext = bytes(
            byte ^ key[index % len(key)] for index, byte in enumerate(cipher)
        ).decode("utf-8")
        return dict(json.loads(plaintext))
