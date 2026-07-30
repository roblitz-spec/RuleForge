"""Tests for M10 Phase 2: RuleSession, ExamplePreview, SessionValidation."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from editor.domain_validator import ValidationIssue, ValidationSeverity
from engine.preview_pipeline import ExamplePreviewResult, PreviewEntry, preview_rule
from engine.rule_inference import infer_rule
from engine.rule_session import RuleSession
from models.inferred_rule import InferredRule
from models.rule import Rule
from models.rule_lifecycle import RuleLifecycle
from models.rule_step import RuleStep
from models.session_validation import SessionValidationResult
from storage.inferred_rule_store import InferredRuleStore


# ── SessionValidationResult ───────────────────────────────────────

class TestSessionValidationResult:
    def test_default_valid(self) -> None:
        r = SessionValidationResult()
        assert r.is_valid
        assert r.error_count == 0

    def test_add_issue(self) -> None:
        r = SessionValidationResult()
        r.add_issue(ValidationIssue(field="x", message="bad"))
        assert not r.is_valid
        assert r.error_count == 1

    def test_add_session_error(self) -> None:
        r = SessionValidationResult()
        r.add_session_error("empty rule")
        assert not r.is_valid
        assert r.error_count == 1

    def test_merge(self) -> None:
        a = SessionValidationResult()
        a.add_issue(ValidationIssue(field="a", message="issue a"))
        b = SessionValidationResult()
        b.add_session_error("error b")
        a.merge(b)
        assert not a.is_valid
        assert a.error_count == 2


# ── ExamplePreview ────────────────────────────────────────────────

class TestPreviewPipeline:
    def test_basic_preview(self) -> None:
        rule = Rule(id="r1", name="Upper", steps=[
            RuleStep(type="case", parameters={"mode": "upper"}),
        ])
        result = preview_rule(rule, ["hello", "world"])
        assert result.total == 2
        assert result.entries[0].output_text == "HELLO"
        assert result.entries[1].output_text == "WORLD"
        assert result.entries[0].match is None  # no expected

    def test_preview_with_expected(self) -> None:
        rule = Rule(id="r1", name="Upper", steps=[
            RuleStep(type="case", parameters={"mode": "upper"}),
        ])
        result = preview_rule(rule, ["hello", "world"], ["HELLO", "WORLD"])
        assert result.all_match
        assert result.matched == 2
        assert result.failed == 0

    def test_preview_with_mismatch(self) -> None:
        rule = Rule(id="r1", name="Upper", steps=[
            RuleStep(type="case", parameters={"mode": "upper"}),
        ])
        result = preview_rule(rule, ["hello"], ["wrong"])
        assert not result.all_match
        assert result.matched == 0
        assert result.failed == 1
        assert result.entries[0].match is False

    def test_empty_rule_no_change(self) -> None:
        rule = Rule(id="r1", name="Empty", steps=[])
        result = preview_rule(rule, ["hello", "world"])
        assert result.entries[0].output_text == "hello"
        assert result.entries[1].output_text == "world"

    def test_multi_step_preview(self) -> None:
        rule = Rule(id="r1", name="Multi", steps=[
            RuleStep(type="case", parameters={"mode": "upper"}),
            RuleStep(type="replace", parameters={"from": " ", "to": "_"}),
        ])
        result = preview_rule(rule, ["hello world"], ["HELLO_WORLD"])
        assert result.all_match


# ── RuleSession ───────────────────────────────────────────────────

class TestRuleSessionLifecycle:
    def test_open_and_lifecycle(self) -> None:
        ir = infer_rule([("hello", "HELLO")], name="Test")
        assert ir is not None

        session = RuleSession()
        session.open(ir)
        assert session.lifecycle == RuleLifecycle.INFERRED
        session.close()

    def test_close_twice_idempotent(self) -> None:
        ir = infer_rule([("a", "A")], name="T")
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        session.close()
        session.close()  # idempotent

    def test_cannot_open_twice(self) -> None:
        ir = infer_rule([("a", "A")], name="T")
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        with pytest.raises(RuntimeError):
            session.open(ir)

    def test_edit_then_validate(self) -> None:
        ir = infer_rule([("hello", "HELLO")], name="Test")
        assert ir is not None
        session = RuleSession()
        session.open(ir)

        result = session.validate()
        assert result.is_valid

        session.close()

    def test_empty_rule_validation_fails(self) -> None:
        rule = Rule(id="r1", name="Empty", steps=[])
        ir = InferredRule(rule=rule)
        session = RuleSession()
        session.open(ir)

        result = session.validate()
        assert not result.is_valid
        assert result.error_count >= 1

        session.close()

    def test_preview_from_source_examples(self) -> None:
        ir = infer_rule([("hello", "HELLO"), ("world", "WORLD")], name="Upper")
        assert ir is not None
        session = RuleSession()
        session.open(ir)

        preview = session.preview()
        assert preview.total == 2
        assert preview.all_match

        session.close()

    def test_preview_with_custom_examples(self) -> None:
        ir = infer_rule([("hello", "HELLO")], name="Upper")
        assert ir is not None
        session = RuleSession()
        session.open(ir)

        preview = session.preview(["abc", "xyz"])
        assert preview.total == 2
        assert preview.entries[0].output_text == "ABC"

        session.close()

    def test_commit_transitions_to_tested(self) -> None:
        ir = infer_rule([("hello", "HELLO")], name="Test")
        assert ir is not None
        session = RuleSession()
        session.open(ir)

        assert session.lifecycle == RuleLifecycle.INFERRED
        session.commit()
        assert session.lifecycle == RuleLifecycle.TESTED

        session.close()

    def test_cannot_commit_without_open(self) -> None:
        session = RuleSession()
        with pytest.raises(RuntimeError):
            session.commit()

    def test_finalize_to_executable_with_store(self) -> None:
        ir = infer_rule([("hello", "HELLO")], name="Test")
        assert ir is not None

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rules.json"
            store = InferredRuleStore(path)

            session = RuleSession()
            session.open(ir, store)
            session.commit()
            session.finalize()

            assert session.lifecycle == RuleLifecycle.EXECUTABLE

            # Verify persisted
            loaded = store.load_all()
            assert len(loaded) == 1
            assert loaded[0].lifecycle == RuleLifecycle.EXECUTABLE

            session.close()

    def test_finalize_without_store_no_error(self) -> None:
        ir = infer_rule([("hello", "HELLO")], name="Test")
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        session.commit()
        session.finalize()  # no store — should not crash
        assert session.lifecycle == RuleLifecycle.EXECUTABLE
        session.close()

    def test_revert_discards_changes(self) -> None:
        ir = infer_rule([("hello", "HELLO")], name="Upper")
        assert ir is not None
        session = RuleSession()
        session.open(ir)

        original_mode = session.rule.steps[0].parameters["mode"]
        session.edit_step(session.rule.steps[0].id, "mode", "lower")
        assert session.is_dirty

        session.revert()
        assert not session.is_dirty
        assert session.rule.steps[0].parameters["mode"] == original_mode

        session.close()

    def test_undo_redo(self) -> None:
        ir = infer_rule([("hello", "HELLO")], name="Test")
        assert ir is not None
        session = RuleSession()
        session.open(ir)

        step_id = session.rule.steps[0].id
        session.edit_step(step_id, "mode", "lower")
        assert session.can_undo

        session.undo()
        assert session.rule.steps[0].parameters["mode"] == "upper"

        session.redo()
        assert session.rule.steps[0].parameters["mode"] == "lower"

        session.close()

    def test_full_workflow(self) -> None:
        """End-to-end: infer → open → edit → validate → preview → commit → finalize."""
        ir = infer_rule([("hello world", "HELLO_WORLD"), ("foo bar", "FOO_BAR")],
                        name="Uppercase+Underscore")
        assert ir is not None

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rules.json"
            store = InferredRuleStore(path)

            session = RuleSession()
            session.open(ir, store)

            # Validate
            assert session.validate().is_valid

            # Preview
            preview = session.preview()
            assert preview.all_match

            # Commit → TESTED
            session.commit()
            assert session.lifecycle == RuleLifecycle.TESTED

            # Finalize → EXECUTABLE + persist
            session.finalize()
            assert session.lifecycle == RuleLifecycle.EXECUTABLE

            # Verify persistence
            loaded = store.load_all()
            assert len(loaded) == 1
            assert loaded[0].lifecycle == RuleLifecycle.EXECUTABLE

            session.close()

    def test_save_without_lifecycle_change(self) -> None:
        ir = infer_rule([("a", "A")], name="Test")
        assert ir is not None

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rules.json"
            store = InferredRuleStore(path)

            session = RuleSession()
            session.open(ir, store)
            session.save()

            loaded = store.load_all()
            assert len(loaded) == 1
            assert loaded[0].lifecycle == RuleLifecycle.INFERRED  # unchanged

            session.close()

    def test_source_examples_preserved(self) -> None:
        pairs = [("hello", "HELLO"), ("world", "WORLD")]
        ir = infer_rule(pairs, name="Upper")
        assert ir is not None
        session = RuleSession()
        session.open(ir)
        assert session.source_examples == pairs
        session.close()


# ── PreviewEntry ──────────────────────────────────────────────────

class TestPreviewEntry:
    def test_match_true(self) -> None:
        e = PreviewEntry(input_text="a", output_text="A", expected="A", match=True)
        assert e.match is True

    def test_match_false(self) -> None:
        e = PreviewEntry(input_text="a", output_text="A", expected="B", match=False)
        assert e.match is False

    def test_match_none_when_no_expected(self) -> None:
        e = PreviewEntry(input_text="a", output_text="A")
        assert e.match is None
