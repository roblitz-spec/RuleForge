"""SessionStore — persists and restores editing sessions (WP-12).

Session persistence is NOT Repository persistence.
SessionStore owns session-only state; Repository owns committed domain state.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from models.rule import Rule
from models.rule_step import RuleStep
from models.session import SerializableSession


class SessionStore:
    """Persists EditSession state to disk.

    Does NOT own WorkingCopy mutation, Undo history, or Commit logic.
    These remain EditSession responsibilities.
    """

    def __init__(self, directory: Path) -> None:
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self._dir / f"{session_id}.json"

    def save(self, session_id: str, data: SerializableSession) -> None:
        """Persist session state to a JSON file."""
        payload = _serialize(data)
        self._path(session_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, session_id: str) -> SerializableSession | None:
        """Restore session state from a JSON file, or None if not found."""
        path = self._path(session_id)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return _deserialize(payload)

    def remove(self, session_id: str) -> None:
        """Delete persisted session state."""
        path = self._path(session_id)
        if path.exists():
            path.unlink()


def _serialize(data: SerializableSession) -> dict:
    wc = data.working_copy
    return {
        "working_copy": {
            "id": wc.id,
            "name": wc.name,
            "description": wc.description,
            "pinned": wc.pinned,
            "steps": [
                {"type": s.type, "parameters": s.parameters, "id": s.id}
                for s in wc.steps
            ],
        },
        "is_dirty": data.is_dirty,
    }


def _deserialize(payload: dict) -> SerializableSession:
    wc_data = payload["working_copy"]
    steps = [
        RuleStep(type=s["type"], parameters=s["parameters"], id=s["id"])
        for s in wc_data["steps"]
    ]
    wc = Rule(
        id=wc_data["id"],
        name=wc_data["name"],
        description=wc_data.get("description", ""),
        pinned=wc_data.get("pinned", False),
        steps=steps,
    )
    return SerializableSession(
        working_copy=wc,
        is_dirty=payload.get("is_dirty", False),
    )
