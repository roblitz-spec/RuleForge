"""Tests for M10.5-B: RuleSession lifecycle and SessionState transitions."""
from __future__ import annotations

import pytest

from engine.rule_inference import infer_rule
from engine.rule_session import RuleSession
from models.session_state import (
    SessionState,
    InvalidStateTransition,
    can_transition,
    transition,
)


# ── SessionState unit tests ───────────────────────────────────────

class TestSessionStateEnum:
    def test_all_states_defined(self) -> None:
        assert {s.name for s in SessionState} == {
            "NEW",
            "INFERRED",
            "EDITING",
            "VALIDATED",
            "PREVIEW_READY",
            "COMMITTED",
            "EXECUTED",
        }


class TestTransitionMap:
    def test_new_only_to_inferred(self) -> None:
        assert can_transition(SessionState.NEW, SessionState.INFERRED)
        assert not can_transition(SessionState.NEW, SessionState.EDITING)
        assert not can_transition(SessionState.NEW, SessionState.EXECUTED)

    def test_inferred_reachable_states(self) -> None:
        assert can_transition(SessionState.INFERRED, SessionState.EDITING)
        assert can_transition(SessionState.INFERRED, SessionState.VALIDATED)
        assert can_transition(SessionState.INFERRED, SessionState.PREVIEW_READY)
        assert can_transition(SessionState.INFERRED, SessionState.COMMITTED)
        assert not can_transition(SessionState.INFERRED, SessionState.EXECUTED)
        assert not can_transition(SessionState.INFERRED, SessionState.NEW)

    def test_editing_reachable_states(self) -> None:
        assert can_transition(SessionState.EDITING, SessionState.VALIDATED)
        assert can_transition(SessionState.EDITING, SessionState.PREVIEW_READY)
        assert not can_transition(SessionState.EDITING, SessionState.COMMITTED)

    def test_validated_reachable_states(self) -> None:
        assert can_transition(SessionState.VALIDATED, SessionState.EDITING)
        assert can_transition(SessionState.VALIDATED, SessionState.PREVIEW_READY)
        assert not can_transition(SessionState.VALIDATED, SessionState.COMMITTED)

    def test_preview_ready_reachable_states(self) -> None:
        assert can_transition(SessionState.PREVIEW_READY, SessionState.EDITING)
        assert can_transition(SessionState.PREVIEW_READY, SessionState.VALIDATED)
        assert can_transition(SessionState.PREVIEW_READY, SessionState.COMMITTED)

    def test_committed_reachable_states(self) -> None:
        assert can_transition(SessionState.COMMITTED, SessionState.EDITING)
        assert can_transition(SessionState.COMMITTED, SessionState.EXECUTED)
        assert not can_transition(SessionState.COMMITTED, SessionState.NEW)

    def test_executed_is_terminal(self) -> None:
        assert not can_transition(SessionState.EXECUTED, SessionState.EDITING)
        assert not can_transition(SessionState.EXECUTED, SessionState.COMMITTED)
        assert not can_transition(SessionState.EXECUTED, SessionState.NEW)


class TestTransitionFunction:
    def test_valid_transition_returns_target(self) -> None:
        assert transition(SessionState.NEW, SessionState.INFERRED) == SessionState.INFERRED

    def test_invalid_transition_raises(self) -> None:
        with pytest.raises(InvalidStateTransition) as exc:
            transition(SessionState.EXECUTED, SessionState.EDITING)
        assert "EXECUTED" in str(exc.value)
        assert "EDITING" in str(exc.value)

    def test_invalid_transition_message_is_descriptive(self) -> None:
        with pytest.raises(InvalidStateTransition) as exc:
            transition(SessionState.NEW, SessionState.COMMITTED)
        assert "NEW" in str(exc.value)
        assert "COMMITTED" in str(exc.value)


# ── RuleSession lifecycle integration ─────────────────────────────

class TestRuleSessionStateProgression:
    """Verify that RuleSession operations advance SessionState correctly."""

    def test_initial_state_is_new(self) -> None:
        session = RuleSession()
        assert session.state == SessionState.NEW

    def test_open_advances_to_inferred(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        assert session.state == SessionState.INFERRED
        session.close()

    def test_edit_advances_to_editing(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        session.edit_step(ir.rule.steps[0].id, "mode", "lower")
        assert session.state == SessionState.EDITING
        session.close()

    def test_validate_advances_to_validated(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        result = session.validate()
        assert result.is_valid
        assert session.state == SessionState.VALIDATED
        session.close()

    def test_preview_advances_to_preview_ready(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        session.preview()
        assert session.state == SessionState.PREVIEW_READY
        session.close()

    def test_commit_advances_to_committed(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        session.commit()
        assert session.state == SessionState.COMMITTED
        session.close()

    def test_finalize_advances_to_executed(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        session.commit()
        session.finalize()
        assert session.state == SessionState.EXECUTED
        session.close()

    def test_full_linear_workflow(self) -> None:
        """Complete NEW → EXECUTED without backtracking."""
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        assert session.state == SessionState.NEW

        session.open(ir)
        assert session.state == SessionState.INFERRED

        session.edit_step(ir.rule.steps[0].id, "mode", "lower")
        assert session.state == SessionState.EDITING

        assert session.validate().is_valid
        assert session.state == SessionState.VALIDATED

        session.preview()
        assert session.state == SessionState.PREVIEW_READY

        session.commit()
        assert session.state == SessionState.COMMITTED

        session.finalize()
        assert session.state == SessionState.EXECUTED

        session.close()


class TestRuleSessionInvalidTransitions:
    """Invalid transitions raise InvalidStateTransition."""

    @pytest.fixture
    def inferred_rule(self):
        return infer_rule([("hello", "HELLO")])

    def test_cannot_edit_before_open(self, inferred_rule) -> None:
        session = RuleSession()
        with pytest.raises(InvalidStateTransition):
            session.edit_step("any", "mode", "upper")

    def test_cannot_finalize_before_commit(self, inferred_rule) -> None:
        assert inferred_rule is not None
        session = RuleSession()
        session.open(inferred_rule)
        with pytest.raises(InvalidStateTransition):
            session.finalize()
        session.close()

    def test_cannot_execute_after_executed(self, inferred_rule) -> None:
        assert inferred_rule is not None
        session = RuleSession()
        session.open(inferred_rule)
        session.commit()
        session.finalize()
        # EXECUTED is terminal
        with pytest.raises(InvalidStateTransition):
            session.commit()
        session.close()


class TestRuleSessionNoAdvanceOnFailure:
    """Failed operations must not advance state."""

    def test_validate_does_not_advance_on_failure(self) -> None:
        """Empty rule validation fails, state stays unchanged."""
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        # Create rule with no steps
        from models.rule import Rule
        from models.rule_lifecycle import RuleLifecycle
        from models.inferred_rule import InferredRule

        bad_ir = InferredRule(
            rule=Rule(id="bad-rule", name="Bad", steps=[]),
            source_examples=[("x", "y")],
            lifecycle=RuleLifecycle.INFERRED,
        )

        session = RuleSession()
        session.open(bad_ir)
        state_before = session.state
        result = session.validate()
        assert not result.is_valid
        assert session.state == state_before  # No advance
        session.close()

    def test_editing_allows_multiple_edits(self) -> None:
        """Repeated edits keep state at EDITING."""
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        step_id = ir.rule.steps[0].id

        session.edit_step(step_id, "mode", "upper")
        assert session.state == SessionState.EDITING

        session.edit_step(step_id, "mode", "lower")
        assert session.state == SessionState.EDITING  # Still editing

        session.close()


class TestRuleSessionBacktracking:
    """Valid backtracking transitions (e.g., PREVIEW_READY → EDITING)."""

    def test_preview_ready_to_editing(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        session.preview()
        assert session.state == SessionState.PREVIEW_READY

        # Go back to editing
        session.edit_step(ir.rule.steps[0].id, "mode", "lower")
        assert session.state == SessionState.EDITING
        session.close()

    def test_committed_to_editing(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        session.commit()
        assert session.state == SessionState.COMMITTED

        # Re-open for editing
        session.edit_step(ir.rule.steps[0].id, "mode", "lower")
        assert session.state == SessionState.EDITING
        session.close()


# ── RuleWorkflow state integration ────────────────────────────────

class TestWorkflowStateIntegration:
    """RuleWorkflow respects RuleSession state."""

    def test_run_sets_session_to_executed(self) -> None:
        from engine.rule_workflow import RuleWorkflow

        wf = RuleWorkflow()
        ir = wf.infer([("hello", "HELLO")])
        assert ir is not None

        session = wf.open_session(ir)
        assert session.state == SessionState.INFERRED

        session.validate()
        session.preview()
        session.commit()
        session.finalize()
        assert session.state == SessionState.EXECUTED
        session.close()

    def test_run_pipeline_produces_executed_state(self) -> None:
        from engine.rule_workflow import RuleWorkflow

        wf = RuleWorkflow()
        result = wf.run([("test", "TEST")])
        assert result.success
