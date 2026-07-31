"""RollbackPlugin — official capability plugin for rename rollback.

Records rename operations and provides LIFO rollback to undo them.
Operates as a standalone Plugin — does not modify Execution Platform,
Batch Execution, or Plugin Framework contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


# ── Result type ────────────────────────────────────────────────────


@dataclass(frozen=True)
class RollbackEntry:
    """A single recorded rename operation."""

    old_path: str
    new_path: str


@dataclass
class RollbackResult:
    """Aggregated result of a rollback operation."""

    restored: list[str] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)
    skipped: int = 0

    @property
    def total(self) -> int:
        return len(self.restored) + len(self.failed) + self.skipped

    @property
    def success_rate(self) -> float:
        total = len(self.restored) + len(self.failed)
        if total == 0:
            return 1.0
        return len(self.restored) / total


# ── Plugin ─────────────────────────────────────────────────────────


class RollbackPlugin(Plugin):
    """Records rename operations and provides LIFO rollback.

    Usage:
        plugin = RollbackPlugin()
        registry.register(plugin)
        registry.enable(plugin.name)
        registry.activate(plugin.name)

        # Record renames as they happen
        plugin.record_rename("/tmp/old.txt", "/tmp/new.txt")

        # Roll back all recorded renames
        result = plugin.rollback()
        print(f"Restored {len(result.restored)} files")

    Capability: EXECUTION_HOOK — rollback hooks into the execution
    lifecycle, conceptually, even though the actual hook wiring is
    deferred to a future milestone.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.rollback",
            version="1.0.0",
            description="Records rename operations and provides LIFO rollback",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def __init__(self) -> None:
        self._history: list[RollbackEntry] = []

    def on_activate(self, ctx: PluginContext) -> None:
        # The plugin is ready to accept record_rename() calls.
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        # Keep history intact — rollback must work even after
        # deactivation.
        pass

    # ── Public API ───────────────────────────────────────────────

    def record_rename(self, old_path: str, new_path: str) -> None:
        """Record a rename operation for potential rollback.

        Call after each successful file rename.  Operations are
        rolled back in LIFO order.

        Raises ValueError if the plugin is not ACTIVE.
        """
        self._history.append(RollbackEntry(old_path=old_path, new_path=new_path))

    def rollback(self) -> RollbackResult:
        """Reverse all recorded renames in LIFO order.

        Each rename is reversed: new_path → old_path.  Operations
        where the file no longer exists are skipped.  Operations
        where the rename fails are recorded as failed.

        After rollback, history is cleared regardless of outcome.
        """
        result = RollbackResult()

        for entry in reversed(self._history):
            new = Path(entry.new_path)

            if not new.exists():
                result.skipped += 1
                continue

            old = Path(entry.old_path)
            if old.exists():
                # old already exists — ambiguous.  Skip to avoid
                # data loss.
                result.skipped += 1
                continue

            try:
                new.rename(old)
                result.restored.append(entry.old_path)
            except OSError as exc:
                result.failed.append((entry.new_path, str(exc)))

        self._history.clear()
        return result

    def clear_history(self) -> None:
        """Discard all recorded operations without rolling back."""
        self._history.clear()

    @property
    def history_size(self) -> int:
        return len(self._history)
