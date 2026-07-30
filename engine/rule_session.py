"""RuleSession — canonical workflow for editing, validating, previewing,
and committing inferred rules.

The RuleSession is the single mutable layer between the Rule domain
model and future IDE/CLI/API interfaces.  All interactive rule
manipulation flows through the session.

Lifecycle (SessionState):
  NEW → INFERRED → EDITING → VALIDATED → PREVIEW_READY → COMMITTED → EXECUTED
"""
from __future__ import annotations

from dataclasses import dataclass, field

from editor.domain_validator import DomainValidator
from editor.edit_session import EditSession
from engine.preview_pipeline import ExamplePreviewResult, preview_rule
from models.inferred_rule import InferredRule
from models.rule import Rule
from models.rule_lifecycle import RuleLifecycle
from models.session_state import SessionState, InvalidStateTransition, transition
from models.session_validation import SessionValidationResult
from storage.inferred_rule_store import InferredRuleStore


@dataclass
class RuleSession:
    """Canonical editing workflow for an InferredRule.

    Wraps EditSession for working-copy management, DomainValidator for
    validation, and preview_pipeline for example-based testing.

    SessionState is enforced at every operation boundary —
    invalid transitions raise InvalidStateTransition.

    Usage:
        session = RuleSession()
        session.open(inferred_rule, store)
        session.edit_step(step_id, "mode", "upper")
        if session.validate().is_valid:
            session.commit()
            session.finalize()
        session.close()
    """

    _inferred_rule: InferredRule | None = field(default=None, init=False, repr=False)
    _edit_session: EditSession = field(default_factory=EditSession, init=False, repr=False)
    _store: InferredRuleStore | None = field(default=None, init=False, repr=False)
    _closed: bool = field(default=False, init=False)
    _state: SessionState = field(default=SessionState.NEW, init=False)

    # ── State management ─────────────────────────────────────────

    def _advance(self, target: SessionState) -> None:
        """Validate and perform a state transition."""
        self._state = transition(self._state, target)

    # ── Lifecycle ────────────────────────────────────────────────

    def open(
        self,
        inferred_rule: InferredRule,
        store: InferredRuleStore | None = None,
    ) -> None:
        """Open a RuleSession for an InferredRule.

        The InferredRule's Rule is deep-copied into the EditSession
        working copy.  The original is preserved until commit().

        Advances state: NEW → INFERRED.
        """
        if self._inferred_rule is not None:
            raise RuntimeError("Session already open — close first")
        self._inferred_rule = inferred_rule
        self._edit_session.open(inferred_rule.rule)
        self._store = store
        self._closed = False
        self._advance(SessionState.INFERRED)

    def close(self) -> None:
        """Close the session.  Idempotent."""
        self._edit_session.close()
        self._closed = True

    # ── Properties ───────────────────────────────────────────────

    @property
    def rule(self) -> Rule:
        """Current working copy of the Rule (from EditSession)."""
        return self._edit_session.rule

    @property
    def lifecycle(self) -> RuleLifecycle:
        if self._inferred_rule is None:
            raise RuntimeError("Session not open")
        return self._inferred_rule.lifecycle

    @property
    def state(self) -> SessionState:
        """Current operational state of the session."""
        return self._state

    @property
    def is_dirty(self) -> bool:
        return self._edit_session.is_dirty()

    @property
    def can_undo(self) -> bool:
        return self._edit_session.can_undo()

    @property
    def can_redo(self) -> bool:
        return self._edit_session.can_redo()

    @property
    def source_examples(self) -> list[tuple[str, str]]:
        if self._inferred_rule is None:
            return []
        return list(self._inferred_rule.source_examples)

    # ── Editing ──────────────────────────────────────────────────

    def edit_step(self, step_id: str, key: str, value: object) -> None:
        """Update a parameter on a RuleStep in the working copy.

        Advances state to EDITING (unless already EDITING).
        """
        if self._state != SessionState.EDITING:
            self._advance(SessionState.EDITING)
        self._edit_session.update_param(step_id, key, value)

    def undo(self) -> None:
        if self._state != SessionState.EDITING:
            self._advance(SessionState.EDITING)
        self._edit_session.undo()

    def redo(self) -> None:
        if self._state != SessionState.EDITING:
            self._advance(SessionState.EDITING)
        self._edit_session.redo()

    # ── Validation ───────────────────────────────────────────────

    def validate(self) -> SessionValidationResult:
        """Validate the current working rule.

        Combines domain-level validation (DomainValidator) with
        session-level checks (empty rule, lifecycle).

        Advances state to VALIDATED on success.
        Does NOT advance on failure.
        """
        result = SessionValidationResult()
        rule = self.rule

        # Session-level checks
        if not rule.steps:
            result.add_session_error("Rule has no steps — nothing to execute")

        # Domain-level checks
        for issue in DomainValidator.validate_rule(rule):
            result.add_issue(issue)

        if result.is_valid:
            self._advance(SessionState.VALIDATED)

        return result

    # ── Preview ──────────────────────────────────────────────────

    def preview(
        self,
        examples: list[str] | None = None,
    ) -> ExamplePreviewResult:
        """Apply the current rule to example inputs.

        If *examples* is None, uses the source examples from the
        InferredRule (with expected outputs for comparison).

        Advances state to PREVIEW_READY on success.

        Args:
            examples: List of input strings to preview.
                      If None, uses source examples from inference.

        Returns:
            ExamplePreviewResult with predicted outputs and comparison.
        """
        if examples is not None:
            result = preview_rule(self.rule, examples)
        elif self._inferred_rule is not None and self._inferred_rule.source_examples:
            originals = [o for o, _ in self._inferred_rule.source_examples]
            expected = [d for _, d in self._inferred_rule.source_examples]
            result = preview_rule(self.rule, originals, expected)
        else:
            result = ExamplePreviewResult()

        self._advance(SessionState.PREVIEW_READY)
        return result

    # ── Commit / Finalize ────────────────────────────────────────

    def commit(self) -> None:
        """Persist working copy to the original Rule.

        Advances state to COMMITTED and RuleLifecycle to TESTED.
        """
        if self._inferred_rule is None:
            raise RuntimeError("Session not open")
        self._edit_session.commit()
        self._inferred_rule.promote_to(RuleLifecycle.TESTED)
        self._advance(SessionState.COMMITTED)

    def finalize(self) -> None:
        """Advance to EXECUTED and persist to store (if available).

        Advances SessionState to EXECUTED and RuleLifecycle to EXECUTABLE.
        """
        if self._inferred_rule is None:
            raise RuntimeError("Session not open")
        self._inferred_rule.promote_to(RuleLifecycle.EXECUTABLE)
        if self._store is not None:
            self._store.save(self._inferred_rule)
        self._advance(SessionState.EXECUTED)

    def revert(self) -> None:
        """Discard all uncommitted changes, return to last committed state."""
        self._edit_session.discard()

    def save(self) -> None:
        """Persist current state to store without changing lifecycle."""
        if self._store is not None and self._inferred_rule is not None:
            self._store.save(self._inferred_rule)
