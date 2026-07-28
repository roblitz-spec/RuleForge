"""EditSession — rule editing session lifecycle (Master Design Section 4.1)."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, auto

from models.rule import Rule
from models.rule_step import RuleStep


class SessionState(Enum):
    """Editing session lifecycle states."""

    CREATED = auto()  # session object exists, not yet opened
    ACTIVE = auto()   # editing in progress
    CLOSED = auto()   # session terminated


def _steps_equal(a: list[RuleStep], b: list[RuleStep]) -> bool:
    """Structural equality of step lists for dirty comparison."""
    if len(a) != len(b):
        return False
    for sa, sb in zip(a, b):
        if sa.type != sb.type or sa.parameters != sb.parameters:
            return False
    return True


@dataclass
class EditSession:
    """Owns the lifecycle of a single rule editing session.

    WP-4 (skeleton): lifecycle, API contract, rule reference.
    WP-5 (WorkingCopy): deep copy on open, mutation isolation, dirty tracking.
    WP-7 (commit): explicit Commit boundary.
    WP-8 (undo/redo): snapshot-based history, session-local, cleared on commit.
    """

    _working_copy: Rule | None = field(default=None, init=False, repr=False)
    _original: Rule | None = field(default=None, init=False, repr=False)
    _dirty: bool = field(default=False, init=False, repr=False)
    _state: SessionState = field(default=SessionState.CREATED, init=False)
    _history: list[Rule] = field(default_factory=list, init=False, repr=False)
    _future: list[Rule] = field(default_factory=list, init=False, repr=False)

    # ── Lifecycle ────────────────────────────────────────────────

    def open(self, rule: Rule) -> None:
        """Begin editing *rule*.

        Creates an isolated WorkingCopy (deep copy).  The original Rule is
        preserved unchanged for the lifetime of the session.
        """
        if self._state is not SessionState.CREATED:
            raise RuntimeError(
                f"Cannot open session in state {self._state.name}",
            )
        self._original = rule
        self._working_copy = deepcopy(rule)
        self._dirty = False
        self._history.clear()
        self._future.clear()
        self._state = SessionState.ACTIVE

    def close(self) -> None:
        """Terminate the session.  Idempotent."""
        self._state = SessionState.CLOSED

    # ── Queries ──────────────────────────────────────────────────

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def rule(self) -> Rule:
        """The WorkingCopy being edited.  Raises if session is not ACTIVE."""
        if self._state is not SessionState.ACTIVE:
            raise RuntimeError(
                f"Session is {self._state.name}, not ACTIVE",
            )
        assert self._working_copy is not None
        return self._working_copy

    @property
    def original(self) -> Rule:
        """The original (committed) Rule — never mutated."""
        if self._original is None:
            raise RuntimeError("No original rule — session never opened")
        return self._original

    # ── Editing hooks ────────────────────────────────────────────

    def update_param(self, step_id: str, key: str, value: object) -> None:
        """Apply a parameter change to the WorkingCopy.

        The original Rule is never touched.  A snapshot is taken before the
        mutation to enable undo.
        """
        if self._state is not SessionState.ACTIVE:
            raise RuntimeError(
                f"Session is {self._state.name}, not ACTIVE",
            )
        assert self._working_copy is not None
        self._history.append(deepcopy(self._working_copy))
        self._future.clear()
        for step in self._working_copy.steps:
            if step.id == step_id:
                step.parameters[key] = value
                self._dirty = True
                return
        # Step not found — discard the snapshot we just took
        self._history.pop()
        raise ValueError(f"Step {step_id!r} not found in working copy")

    def is_dirty(self) -> bool:
        """True if any update_param has been called since open, discard, commit, or undo-to-original."""
        return self._dirty

    def discard(self) -> None:
        """Revert WorkingCopy to the original Rule (local only, no persistence)."""
        if self._original is None:
            return
        self._working_copy = deepcopy(self._original)
        self._dirty = False
        self._history.clear()
        self._future.clear()

    def commit(self) -> None:
        """Apply WorkingCopy changes to the original Rule (in-place mutation).

        This is the explicit Commit boundary — the only path from editing state
        to domain state.  After a successful commit:
        - The original Rule reflects the WorkingCopy content.
        - is_dirty() returns False.
        - Undo/redo history is cleared.
        - The WorkingCopy remains the editing target.
        """
        if self._original is None or self._working_copy is None:
            raise RuntimeError("Cannot commit — no active session")
        wc = self._working_copy
        self._original.name = wc.name
        self._original.description = wc.description
        self._original.steps = deepcopy(wc.steps)
        self._original.pinned = wc.pinned
        self._dirty = False
        self._history.clear()
        self._future.clear()

    # ── Undo / Redo (WP-8) ───────────────────────────────────────

    def can_undo(self) -> bool:
        """True if at least one undo snapshot exists."""
        return len(self._history) > 0

    def can_redo(self) -> bool:
        """True if at least one redo snapshot exists."""
        return len(self._future) > 0

    def undo(self) -> None:
        """Restore the WorkingCopy to the previous snapshot."""
        if not self._history:
            return
        self._future.append(self._working_copy)
        self._working_copy = self._history.pop()
        self._dirty = not self._is_clean()

    def redo(self) -> None:
        """Restore the WorkingCopy to the next snapshot."""
        if not self._future:
            return
        self._history.append(self._working_copy)
        self._working_copy = self._future.pop()
        self._dirty = not self._is_clean()

    # ── Helpers ──────────────────────────────────────────────────

    def _is_clean(self) -> bool:
        """True when the WorkingCopy matches the original Rule."""
        if self._original is None or self._working_copy is None:
            return True
        wc = self._working_copy
        og = self._original
        return (
            wc.name == og.name
            and wc.description == og.description
            and wc.pinned == og.pinned
            and _steps_equal(wc.steps, og.steps)
        )
