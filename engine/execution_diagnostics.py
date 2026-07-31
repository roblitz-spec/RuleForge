"""ExecutionDiagnostics — structured diagnostics builder.

Replaces ad-hoc dict manipulation with a consistent, engine-agnostic
structure.  Used by all ExecutionEngine implementations.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExecutionDiagnostics:
    """Structured diagnostics produced by execution engines.

    Engine-agnostic — no subclasses per engine type.  Engine-specific
    details go in `metadata`.
    """

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    journal: list[dict[str, object]] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def add_conflict(self, msg: str) -> None:
        self.conflicts.append(msg)

    def add_journal_entry(self, entry: dict[str, object]) -> None:
        self.journal.append(entry)

    # ── Conversion ────────────────────────────────────────────────

    def to_dict(self) -> dict[str, object]:
        d: dict[str, object] = {}
        if self.errors:
            d["errors"] = list(self.errors)
        if self.warnings:
            d["warnings"] = list(self.warnings)
        if self.conflicts:
            d["conflicts"] = list(self.conflicts)
        if self.journal:
            d["journal"] = list(self.journal)
        if self.metadata:
            d["metadata"] = dict(self.metadata)
        return d
