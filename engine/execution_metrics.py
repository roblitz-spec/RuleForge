"""ExecutionMetrics — structured execution statistics.

Shared across all engines.  Engine-specific extensions go in
the `extra` dict rather than subclasses.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExecutionMetrics:
    """Execution statistics collected during a pipeline run.

    Filesystem engines populate files_* fields; headless engines
    leave them at zero.  Engine-specific metrics go in `extra`.
    """

    files_scanned: int = 0
    files_selected: int = 0
    files_modified: int = 0
    files_skipped: int = 0
    conflict_count: int = 0
    error_count: int = 0
    duration_ms: float = 0.0

    extra: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "files_scanned": self.files_scanned,
            "files_selected": self.files_selected,
            "files_modified": self.files_modified,
            "files_skipped": self.files_skipped,
            "conflict_count": self.conflict_count,
            "error_count": self.error_count,
            "duration_ms": self.duration_ms,
            **self.extra,
        }
