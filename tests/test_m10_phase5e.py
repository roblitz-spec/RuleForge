"""M10.5-E: Public API contract tests.

Verifies the frozen public API contract — behavior, stability,
and documented semantics — without testing implementation details.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import get_type_hints

import pytest

from models.inferred_rule import InferredRule
from models.rule import Rule, RuleStep
from models.rule_lifecycle import RuleLifecycle
from models.session_state import (
    InvalidStateTransition,
    SessionState,
    can_transition,
    transition,
)
from models.session_validation import SessionValidationResult
from engine.preview_pipeline import (
    ExamplePreviewResult,
    PreviewEntry,
    preview_rule,
)
from engine.rule_inference import infer_rule
from engine.rule_inspector import RuleInspection
from engine.rule_session import RuleSession
from engine.rule_workflow import RuleWorkflow, WorkflowResult

PUBLIC_TYPES = [
    RuleWorkflow,
    WorkflowResult,
    RuleSession,
    SessionState,
    InvalidStateTransition,
    SessionValidationResult,
    InferredRule,
    Rule,
    RuleStep,
    RuleLifecycle,
    RuleInspection,
    ExamplePreviewResult,
    PreviewEntry,
]


# ── Public API surface existence ──────────────────────────────────

def test_all_public_types_importable() -> None:
    """Every documented public type imports without error."""
    for t in PUBLIC_TYPES:
        assert t.__name__, f"{t} has no __name__"


# ── WorkflowResult contract ───────────────────────────────────────

class TestWorkflowResultContract:
    def test_default_success_is_true(self) -> None:
        r = WorkflowResult()
        assert r.success is True
        assert r.errors == []

    def test_add_error_sets_success_false(self) -> None:
        r = WorkflowResult()
        r.add_error("something went wrong")
        assert r.success is False
        assert r.errors == ["something went wrong"]

    def test_add_error_accumulates(self) -> None:
        r = WorkflowResult()
        r.add_error("a")
        r.add_error("b")
        assert r.errors == ["a", "b"]
        assert r.success is False

    def test_errors_never_none(self) -> None:
        assert WorkflowResult().errors is not None
        assert WorkflowResult(errors=[]).errors is not None

    def test_default_stage_results_are_none(self) -> None:
        r = WorkflowResult()
        assert r.inferred_rule is None
        assert r.inspection is None
        assert r.validation is None
        assert r.preview is None
        assert r.outputs == []

    def test_type_annotations_match(self) -> None:
        hints = get_type_hints(WorkflowResult)
        assert "inferred_rule" in hints
        assert "success" in hints
        assert hints["success"] is bool


# ── SessionState contract ─────────────────────────────────────────

class TestSessionStateContract:
    def test_canonical_sequence(self) -> None:
        expected = [
            SessionState.NEW,
            SessionState.INFERRED,
            SessionState.EDITING,
            SessionState.VALIDATED,
            SessionState.PREVIEW_READY,
            SessionState.COMMITTED,
            SessionState.EXECUTED,
        ]
        # Verify states exist
        for state in expected:
            assert isinstance(state, SessionState)

    def test_executed_is_terminal(self) -> None:
        assert not can_transition(SessionState.EXECUTED, SessionState.COMMITTED)
        assert not can_transition(SessionState.EXECUTED, SessionState.INFERRED)

    def test_invalid_transition_raises_explicit_type(self) -> None:
        with pytest.raises(InvalidStateTransition) as exc_info:
            transition(SessionState.NEW, SessionState.EXECUTED)
        assert "EXECUTED" in str(exc_info.value) or "Executed" in str(exc_info.value)

    def test_same_state_is_idempotent(self) -> None:
        for state in SessionState:
            result = transition(state, state)
            assert result == state

    def test_commit_requires_preview_or_validated(self) -> None:
        """COMMITTED must follow PREVIEW_READY or VALIDATED."""
        assert can_transition(SessionState.VALIDATED, SessionState.COMMITTED)
        assert can_transition(SessionState.PREVIEW_READY, SessionState.COMMITTED)
        # NEW → COMMITTED is not allowed
        assert not can_transition(SessionState.NEW, SessionState.COMMITTED)


# ── Exception model contract ──────────────────────────────────────

class TestExceptionContract:
    def test_invalid_state_transition_is_exception(self) -> None:
        assert issubclass(InvalidStateTransition, Exception)

    def test_invalid_state_transition_carries_message(self) -> None:
        exc = InvalidStateTransition("from NEW to EXECUTED")
        assert "NEW" in str(exc)
        assert "EXECUTED" in str(exc)

    def test_only_known_public_exceptions_exist(self) -> None:
        """Verify we don't accidentally leak new exception types."""
        from models import session_state
        public_exceptions = [
            obj for name in dir(session_state)
            if isinstance(obj := getattr(session_state, name), type)
            and issubclass(obj, Exception)
        ]
        # Only InvalidStateTransition should be public
        assert set(public_exceptions) == {InvalidStateTransition}


# ── RuleWorkflow contract ─────────────────────────────────────────

class TestRuleWorkflowContract:
    EXAMPLES: list[tuple[str, str]] = [("hello", "HELLO"), ("world", "WORLD")]

    def test_infer_returns_inferred_rule_or_none(self) -> None:
        ir = RuleWorkflow.infer(self.EXAMPLES)
        assert isinstance(ir, InferredRule)

    def test_infer_identical_returns_none(self) -> None:
        ir = RuleWorkflow.infer([("hello", "hello")])
        assert ir is None

    def test_run_returns_workflow_result(self) -> None:
        wf = RuleWorkflow()
        result = wf.run(self.EXAMPLES)
        assert isinstance(result, WorkflowResult)
        assert result.success is True

    def test_run_populates_all_stages(self) -> None:
        wf = RuleWorkflow()
        result = wf.run(self.EXAMPLES)
        assert result.inferred_rule is not None
        assert result.inspection is not None
        assert result.validation is not None
        assert result.preview is not None
        assert len(result.outputs) > 0

    def test_run_with_noop_examples(self) -> None:
        wf = RuleWorkflow()
        result = wf.run([("a", "a")])
        assert result.success is False
        assert len(result.errors) > 0

    def test_type_annotations(self) -> None:
        hints = get_type_hints(RuleWorkflow.infer)
        assert hints["examples"] == list[tuple[str, str]]
        assert hints["name"] == str

        hints = get_type_hints(RuleWorkflow.run)
        assert hints["name"] == str


# ── RuleInspection contract ───────────────────────────────────────

class TestRuleInspectionContract:
    def test_inspect_has_step_count(self) -> None:
        ir = infer_rule([("hello", "HELLO"), ("world", "WORLD")])
        assert ir is not None
        insp = RuleInspection.inspect(ir.rule)
        assert insp.step_count >= 1
        assert len(insp.steps) == insp.step_count

    def test_inspect_fields_exist(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        insp = RuleInspection.inspect(ir.rule)
        assert isinstance(insp.step_count, int)
        assert isinstance(insp.steps, list)
        assert isinstance(insp.is_empty, bool)
        assert isinstance(insp.rule_name, str)
        assert isinstance(insp.rule_id, str)


# ── Preview contract ──────────────────────────────────────────────

class TestPreviewContract:
    def test_preview_returns_entries(self) -> None:
        ir = infer_rule([("hello", "HELLO")])
        assert ir is not None
        result = preview_rule(ir.rule, ["hello", "world"])
        assert isinstance(result, ExamplePreviewResult)
        assert len(result.entries) == 2
        assert isinstance(result.entries[0], PreviewEntry)
        assert result.entries[0].input_text == "hello"
        assert result.entries[0].output_text == "HELLO"


# ── CLI → public API consistency ──────────────────────────────────

class TestCLIConsistency:
    """CLI uses only public API — no internal module imports."""

    def test_cli_imports_only_public_api(self) -> None:
        cli_path = Path(__file__).resolve().parent.parent / "cli" / "workflow_cli.py"
        source = cli_path.read_text()

        # Internal modules CLI must NOT import directly
        forbidden = [
            "from engine.rule_session",
            "from models.session_state",
            "from engine.rule_inference",
            "from engine.rule_inspector",
            "from engine.preview_pipeline",
        ]
        for mod in forbidden:
            assert mod not in source, f"CLI imports internal module: {mod}"

        # CLI MUST import RuleWorkflow (the public entry point)
        assert "from engine.rule_workflow import" in source

    def test_infer_json_is_valid(self, tmp_path: Path) -> None:
        """Infer output is machine-readable JSON."""
        r = subprocess.run(
            [sys.executable, "-m", "cli.workflow_cli", "workflow", "infer",
             '[["a","A"]]', "-n", "Test"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parent.parent),
        )
        assert r.returncode == 0
        import json
        data = json.loads(r.stdout)
        assert data["name"] == "Test"
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) >= 1
        assert "type" in data["steps"][0]

    def test_exit_code_zero_on_success(self) -> None:
        r = subprocess.run(
            [sys.executable, "-m", "cli.workflow_cli", "workflow", "run",
             '[["hello","HELLO"]]', "-n", "Test"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parent.parent),
        )
        assert r.returncode == 0

    def test_exit_code_one_on_failure(self) -> None:
        r = subprocess.run(
            [sys.executable, "-m", "cli.workflow_cli", "workflow", "run",
             '[["hello","hello"]]', "-n", "Test"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parent.parent),
        )
        assert r.returncode == 1


# ── Backward compatibility (smoke) ────────────────────────────────

class TestBackwardCompatibility:
    """Verify existing consumer patterns still work."""

    def test_rule_workflow_stage_methods_still_accept_kwargs(self) -> None:
        ir = RuleWorkflow.infer(examples=[("a", "A")], name="Old")
        assert ir is not None
        session = RuleWorkflow.open_session(inferred_rule=ir, store=None)
        assert isinstance(session, RuleSession)
        session.close()

    def test_workflow_run_accepts_store_kwarg(self) -> None:
        wf = RuleWorkflow()
        result = wf.run(examples=[("x", "X")], name="Compat", store=None)
        assert result.success is True
