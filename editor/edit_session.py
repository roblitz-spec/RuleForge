"""EditSession — rule editing session lifecycle (Master Design Section 4.1)."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, auto

from models.rule import Rule


class SessionState(Enum):
    """Editing session lifecycle states."""

    CREATED = auto()  # session object exists, not yet opened
    ACTIVE = auto()   # editing in progress
    CLOSED = auto()   # session terminated


@dataclass
class EditSession:
    """Owns the lifecycle of a single rule editing session.

    WP-4 (skeleton): lifecycle, API contract, rule reference.
    WP-5 (WorkingCopy): deep copy on open, mutation isolation, dirty tracking.
    """

    _working_copy: Rule | None = field(default=None, init=False, repr=False)
    _original: Rule | None = field(default=None, init=False, repr=False)
    _dirty: bool = field(default=False, init=False, repr=False)
    _state: SessionState = field(default=SessionState.CREATED, init=False)

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

        The original Rule is never touched.
        """
        if self._state is not SessionState.ACTIVE:
            raise RuntimeError(
                f"Session is {self._state.name}, not ACTIVE",
            )
        assert self._working_copy is not None
        for step in self._working_copy.steps:
            if step.id == step_id:
                step.parameters[key] = value
                self._dirty = True
                return
        raise ValueError(f"Step {step_id!r} not found in working copy")

    def is_dirty(self) -> bool:
        """True if any update_param has been called since open or discard."""
        return self._dirty

    def discard(self) -> None:
        """Revert WorkingCopy to the original Rule (local only, no persistence).

        WP-5: local revert only.  WP-8 will integrate with RuleRepository.
        """
        if self._original is None:
            return
        self._working_copy = deepcopy(self._original)
        self._dirty = False

    def commit(self) -> None:
        """WP-5 stub — no-op.  WP-8: persist via RuleRepository."""
        raise NotImplementedError("WP-8: save pipeline integration")
