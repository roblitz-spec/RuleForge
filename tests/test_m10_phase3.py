"""Tests for M10.5: RuleWorkflow orchestration layer."""
from __future__ import annotations

import tempfile
from pathlib import Path

from engine.rule_inspector import RuleInspection
from engine.rule_workflow import RuleWorkflow, WorkflowResult
from models.inferred_rule import InferredRule
from models.rule_lifecycle import RuleLifecycle
from storage.inferred_rule_store import InferredRuleStore


# ── WorkflowResult ────────────────────────────────────────────────

class TestWorkflowResult:
    def test_default_success(self) -> None:
        r = WorkflowResult()
        assert r.success
        assert r.errors == []

    def test_add_error(self) -> None:
        r = WorkflowResult()
        r.add_error("something went wrong")
        assert not r.success
        assert r.errors == ["something went wrong"]


# ── Stage methods ─────────────────────────────────────────────────

class TestRuleWorkflowStages:
    def test_infer_returns_inferred_rule(self) -> None:
        wf = RuleWorkflow()
        ir = wf.infer([("hello", "HELLO"), ("world", "WORLD")])
        assert ir is not None
        assert isinstance(ir, InferredRule)
        assert ir.rule.steps[0].type == "case"

    def test_infer_returns_none_for_no_change(self) -> None:
        wf = RuleWorkflow()
        ir = wf.infer([("hello", "hello")])
        assert ir is None

    def test_inspect_returns_structured_info(self) -> None:
        wf = RuleWorkflow()
        ir = wf.infer([("hello", "HELLO")])
        assert ir is not None
        info = wf.inspect(ir.rule)
        assert isinstance(info, RuleInspection)
        assert info.step_count == 1
        assert info.steps[0].step_type == "case"

    def test_execute_applies_rule(self) -> None:
        wf = RuleWorkflow()
        ir = wf.infer([("hello", "HELLO")])
        assert ir is not None
        outputs = wf.execute(ir.rule, ["world", "foo"])
        assert outputs == ["WORLD", "FOO"]

    def test_execute_multi_step(self) -> None:
        wf = RuleWorkflow()
        ir = wf.infer([("hello world", "HELLO_WORLD"), ("foo bar", "FOO_BAR")])
        assert ir is not None
        outputs = wf.execute(ir.rule, ["abc def"])
        assert outputs == ["ABC_DEF"]

    def test_open_session_creates_valid_session(self) -> None:
        wf = RuleWorkflow()
        ir = wf.infer([("hello", "HELLO")])
        assert ir is not None
        session = wf.open_session(ir)
        assert session.lifecycle == RuleLifecycle.INFERRED
        assert session.rule.name == "Inferred Rule"
        session.close()

    def test_open_session_with_store(self) -> None:
        wf = RuleWorkflow()
        ir = wf.infer([("hello", "HELLO")], name="Test")
        assert ir is not None

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rules.json"
            store = InferredRuleStore(path)
            session = wf.open_session(ir, store)
            session.commit()
            session.finalize()
            session.close()

            loaded = store.load_all()
            assert len(loaded) == 1
            assert loaded[0].lifecycle == RuleLifecycle.EXECUTABLE


# ── Full pipeline ─────────────────────────────────────────────────

class TestRuleWorkflowPipeline:
    def test_run_full_pipeline(self) -> None:
        wf = RuleWorkflow()
        pairs = [("hello world", "HELLO_WORLD"), ("foo bar", "FOO_BAR")]
        result = wf.run(pairs, name="UpperUnderscore")

        assert result.success
        assert result.inferred_rule is not None
        assert result.inspection is not None
        assert result.inspection.step_count >= 1
        assert result.validation is not None
        assert result.validation.is_valid
        assert result.preview is not None
        assert result.outputs == ["HELLO_WORLD", "FOO_BAR"]
        assert result.errors == []

    def test_run_no_change_inputs(self) -> None:
        wf = RuleWorkflow()
        result = wf.run([("hello", "hello")])
        assert not result.success
        assert "Inference produced no rule" in result.errors[0]
        assert result.inferred_rule is None

    def test_run_with_store_persists(self) -> None:
        wf = RuleWorkflow()
        pairs = [("hello", "HELLO")]

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rules.json"
            store = InferredRuleStore(path)
            result = wf.run(pairs, name="Upper", store=store)

            assert result.success
            assert result.outputs == ["HELLO"]

            loaded = store.load_all()
            assert len(loaded) == 1
            assert loaded[0].rule.name == "Upper"

    def test_run_rule_is_executable_after(self) -> None:
        wf = RuleWorkflow()
        ir = wf.infer([("a", "A")])
        assert ir is not None
        outputs = wf.execute(ir.rule, ["b", "c"])
        assert outputs == ["B", "C"]

    def test_run_empty_examples(self) -> None:
        wf = RuleWorkflow()
        result = wf.run([])
        assert not result.success


# ── Integration — workflow with edits ─────────────────────────────

class TestWorkflowWithEdits:
    def test_step_by_step_with_edit(self) -> None:
        """Simulate CLI: infer → open → inspect → edit → validate → preview → commit → execute."""
        wf = RuleWorkflow()

        ir = wf.infer([("hello", "HELLO"), ("world", "WORLD")])
        assert ir is not None

        session = wf.open_session(ir)
        info = wf.inspect(session.rule)
        assert info.steps[0].params["mode"] == "upper"

        # Edit: change case mode
        step_id = session.rule.steps[0].id
        session.edit_step(step_id, "mode", "lower")

        # Validate + preview
        assert session.validate().is_valid
        preview = session.preview()
        assert preview.all_match is False  # expected HELLO, got hello

        # Commit + execute
        session.commit()
        outputs = wf.execute(session.rule, ["HELLO", "WORLD"])
        assert outputs == ["hello", "world"]

        session.close()

    def test_inspect_execute_roundtrip(self) -> None:
        """Inspect the inferred rule, execute, verify consistency."""
        wf = RuleWorkflow()
        ir = wf.infer([("test", "TEST")])
        assert ir is not None

        info = wf.inspect(ir.rule)
        assert info.rule_name == "Inferred Rule"

        outputs = wf.execute(ir.rule, ["abc", "xyz"])
        assert outputs == ["ABC", "XYZ"]
