"""SessionState — explicit operational state model for RuleSession.

SessionState is the authoritative workflow state for RuleForge.
Every RuleSession owns one SessionState; RuleWorkflow reads it
but never writes it directly.

Transition rules are enforced — invalid transitions raise
InvalidStateTransition with a descriptive message.
"""
from __future__ import annotations

from enum import Enum, auto


class SessionState(Enum):
    """Operational state of a RuleSession.

    ┌──────────────┐
    │     NEW      │  session created, no rule loaded
    └──────┬───────┘
           │ open()
    ┌──────▼───────┐
    │  INFERRED    │  rule loaded from inference
    └──────┬───────┘
           │ edit_step() / undo() / redo()
    ┌──────▼───────┐
    │  EDITING     │  being modified ──────────────┐
    └──┬───┬───┬───┘                               │
       │   │   └──────────────────┐                 │
       │   │ validate()    preview()                │
       │   ▼                      ▼                 │
       │ ┌──────────┐  ┌────────────────┐          │
       │ │VALIDATED │  │ PREVIEW_READY  │          │
       │ └────┬─────┘  └───┬───┬────┬───┘          │
       │      │            │   │    │              │
       │      └────────────┼───┘    │ commit()     │
       │                   │        │              │
       │     preview()     │        ▼              │
       │                   │  ┌───────────┐        │
       │                   └──►  COMMITTED│        │
       │                      └─────┬─────┘        │
       │                            │ finalize()    │
       │                            ▼               │
       │                      ┌───────────┐        │
       │                      │ EXECUTED  │ (term) │
       │                      └───────────┘        │
       │                                           │
       └───────────────────────────────────────────┘
              edit_step() (re-edit after commit)
    """

    NEW = auto()
    INFERRED = auto()
    EDITING = auto()
    VALIDATED = auto()
    PREVIEW_READY = auto()
    COMMITTED = auto()
    EXECUTED = auto()


# ── Transition map ──────────────────────────────────────────────────
# From each state, which states are reachable with one operation.

_TRANSITIONS: dict[SessionState, frozenset[SessionState]] = {
    SessionState.NEW: frozenset({SessionState.INFERRED}),
    SessionState.INFERRED: frozenset({
        SessionState.EDITING,
        SessionState.VALIDATED,
        SessionState.PREVIEW_READY,
        SessionState.COMMITTED,
    }),
    SessionState.EDITING: frozenset({
        SessionState.EDITING,
        SessionState.VALIDATED,
        SessionState.PREVIEW_READY,
    }),
    SessionState.VALIDATED: frozenset({
        SessionState.EDITING,
        SessionState.PREVIEW_READY,
    }),
    SessionState.PREVIEW_READY: frozenset({
        SessionState.EDITING,
        SessionState.VALIDATED,
        SessionState.COMMITTED,
    }),
    SessionState.COMMITTED: frozenset({
        SessionState.EDITING,
        SessionState.EXECUTED,
    }),
    SessionState.EXECUTED: frozenset(),
}


class InvalidStateTransition(Exception):
    """Raised when a state transition is not allowed."""


def can_transition(current: SessionState, target: SessionState) -> bool:
    """Check whether *current* → *target* is a valid transition."""
    return target in _TRANSITIONS.get(current, frozenset())


def transition(current: SessionState, target: SessionState) -> SessionState:
    """Perform a validated transition.

    Returns *target* if valid; raises InvalidStateTransition otherwise.
    """
    if not can_transition(current, target):
        raise InvalidStateTransition(
            f"Cannot transition from {current.name} to {target.name}"
        )
    return target
