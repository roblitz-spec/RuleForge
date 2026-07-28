"""Serializable session state for persistence (WP-12).

Session persistence restores editing context, not domain state.
"""
from __future__ import annotations

from dataclasses import dataclass

from models.rule import Rule


@dataclass
class SerializableSession:
    """Snapshot of EditSession state suitable for JSON serialization.

    Does NOT include undo/redo history — a restored session starts
    with a clean history by design (WP-12 Option A).
    """

    working_copy: Rule
    is_dirty: bool
