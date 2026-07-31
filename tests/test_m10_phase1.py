"""Tests for M10 Phase 1: RuleLifecycle, InferredRule, RuleInspector, InferredRuleStore."""
from __future__ import annotations

import tempfile
from pathlib import Path

from engine.rule_inference import infer_rule
from engine.rule_inspector import RuleInspection, StepInfo
from models.inferred_rule import InferredRule
from models.rule import Rule
from models.rule_lifecycle import RuleLifecycle
from models.rule_step import RuleStep
from storage.inferred_rule_store import InferredRuleStore


# ── RuleLifecycle ─────────────────────────────────────────────────

class TestRuleLifecycle:
    def test_members(self) -> None:
        assert RuleLifecycle.INFERRED is not None
        assert RuleLifecycle.EDITABLE is not None
        assert RuleLifecycle.TESTED is not None
        assert RuleLifecycle.EXECUTABLE is not None

    def test_is_enum(self) -> None:
        assert isinstance(RuleLifecycle.INFERRED, RuleLifecycle)


# ── InferredRule ──────────────────────────────────────────────────

class TestInferredRule:
    def test_default_lifecycle(self) -> None:
        rule = Rule(id="r1", name="Test", steps=[])
        ir = InferredRule(rule=rule)
        assert ir.lifecycle == RuleLifecycle.INFERRED
        assert ir.name == "Test"
        assert ir.steps == []

    def test_promote(self) -> None:
        rule = Rule(id="r1", name="Test", steps=[])
        ir = InferredRule(rule=rule)
        ir.promote_to(RuleLifecycle.EDITABLE)
        assert ir.lifecycle == RuleLifecycle.EDITABLE
        ir.promote_to(RuleLifecycle.TESTED)
        assert ir.lifecycle == RuleLifecycle.TESTED
        ir.promote_to(RuleLifecycle.EXECUTABLE)
        assert ir.lifecycle == RuleLifecycle.EXECUTABLE

    def test_source_examples(self) -> None:
        rule = Rule(id="r1", name="Test", steps=[])
        ir = InferredRule(
            rule=rule,
            source_examples=[("hello", "HELLO"), ("world", "WORLD")],
        )
        assert len(ir.source_examples) == 2

    def test_created_at(self) -> None:
        import time
        rule = Rule(id="r1", name="Test", steps=[])
        before = time.time()
        ir = InferredRule(rule=rule)
        after = time.time()
        assert before <= ir.created_at <= after

    def test_unique_ids(self) -> None:
        r1 = InferredRule(rule=Rule(id="a", name="A", steps=[]))
        r2 = InferredRule(rule=Rule(id="b", name="B", steps=[]))
        assert r1.id != r2.id


# ── RuleInspector ─────────────────────────────────────────────────

class TestRuleInspector:
    def test_empty_rule(self) -> None:
        rule = Rule(id="r1", name="Empty", steps=[])
        insp = RuleInspection.inspect(rule)
        assert insp.rule_name == "Empty"
        assert insp.step_count == 0
        assert insp.is_empty
        assert len(insp.steps) == 0
        assert len(insp.warnings) >= 1

    def test_replace_step(self) -> None:
        rule = Rule(id="r1", name="R", steps=[
            RuleStep(type="replace", parameters={"from": " ", "to": "_"}),
        ])
        insp = RuleInspection.inspect(rule)
        assert insp.step_count == 1
        assert not insp.is_empty
        s = insp.steps[0]
        assert s.step_type == "replace"
        assert s.index == 0
        assert s.params["from"] == " "
        assert s.params["to"] == "_"
        assert "→" in s.description

    def test_case_step(self) -> None:
        rule = Rule(id="r1", name="R", steps=[
            RuleStep(type="case", parameters={"mode": "upper"}),
        ])
        insp = RuleInspection.inspect(rule)
        s = insp.steps[0]
        assert s.step_type == "case"
        assert s.params["mode"] == "upper"

    def test_multi_step(self) -> None:
        rule = Rule(id="r1", name="Multi", steps=[
            RuleStep(type="case", parameters={"mode": "upper"}),
            RuleStep(type="replace", parameters={"from": " ", "to": "_"}),
            RuleStep(type="add_prefix", parameters={"text": "IMG_"}),
        ])
        insp = RuleInspection.inspect(rule)
        assert insp.step_count == 3
        assert insp.uses_index is False
        assert insp.uses_metadata is False
        assert [s.index for s in insp.steps] == [0, 1, 2]
        assert [s.step_type for s in insp.steps] == ["case", "replace", "add_prefix"]

    def test_number_step_detected(self) -> None:
        rule = Rule(id="r1", name="Num", steps=[
            RuleStep(type="number", parameters={}),
        ])
        insp = RuleInspection.inspect(rule)
        assert insp.uses_index is True

    def test_date_step_detected(self) -> None:
        rule = Rule(id="r1", name="Date", steps=[
            RuleStep(type="date", parameters={}),
        ])
        insp = RuleInspection.inspect(rule)
        assert insp.uses_metadata is True

    def test_unknown_step_type(self) -> None:
        rule = Rule(id="r1", name="Unknown", steps=[
            RuleStep(type="future_type", parameters={"x": "y"}),
        ])
        insp = RuleInspection.inspect(rule)
        assert insp.step_count == 1
        assert insp.steps[0].label == "future_type"  # fallback to type name


# ── infer_rule integration ────────────────────────────────────────

class TestInferRule:
    def test_returns_inferred_rule(self) -> None:
        result = infer_rule([("hello", "HELLO"), ("world", "WORLD")])
        assert result is not None
        assert isinstance(result, InferredRule)
        assert result.lifecycle == RuleLifecycle.INFERRED
        assert len(result.rule.steps) == 1
        assert result.rule.steps[0].type == "case"
        assert result.rule.steps[0].parameters["mode"] == "upper"

    def test_returns_none_when_no_change(self) -> None:
        result = infer_rule([("hello", "hello")])
        assert result is None

    def test_preserves_source_examples(self) -> None:
        pairs = [("hello world", "HELLO_WORLD"), ("foo bar", "FOO_BAR")]
        result = infer_rule(pairs)
        assert result is not None
        assert result.source_examples == pairs

    def test_custom_name(self) -> None:
        result = infer_rule([("a", "A")], name="Uppercase Rule")
        assert result is not None
        assert result.rule.name == "Uppercase Rule"


# ── InferredRuleStore ─────────────────────────────────────────────

class TestInferredRuleStore:
    def test_save_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inferred_rules.json"
            store = InferredRuleStore(path)

            rule = Rule(id="r1", name="Test", steps=[
                RuleStep(type="case", parameters={"mode": "upper"}),
            ])
            ir = InferredRule(rule=rule, source_examples=[("a", "A")])
            store.save(ir)

            loaded = store.load_all()
            assert len(loaded) == 1
            assert loaded[0].id == ir.id
            assert loaded[0].rule.name == "Test"
            assert len(loaded[0].rule.steps) == 1
            assert loaded[0].rule.steps[0].type == "case"

    def test_load_empty(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "nonexistent.json"
            store = InferredRuleStore(path)
            assert store.load_all() == []

    def test_delete(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inferred_rules.json"
            store = InferredRuleStore(path)

            ir = InferredRule(rule=Rule(id="r1", name="T", steps=[]))
            store.save(ir)
            assert len(store.load_all()) == 1

            store.delete(ir.id)
            assert store.load_all() == []

    def test_update_existing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inferred_rules.json"
            store = InferredRuleStore(path)

            ir = InferredRule(rule=Rule(id="r1", name="Original", steps=[]))
            store.save(ir)

            ir.rule.name = "Updated"
            ir.promote_to(RuleLifecycle.TESTED)
            store.save(ir)

            loaded = store.load_all()
            assert len(loaded) == 1
            assert loaded[0].rule.name == "Updated"
            assert loaded[0].lifecycle == RuleLifecycle.TESTED

    def test_multiple_rules(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inferred_rules.json"
            store = InferredRuleStore(path)

            for i in range(3):
                ir = InferredRule(
                    rule=Rule(id=f"r{i}", name=f"Rule {i}", steps=[]),
                )
                store.save(ir)

            loaded = store.load_all()
            assert len(loaded) == 3
            names = {r.rule.name for r in loaded}
            assert names == {"Rule 0", "Rule 1", "Rule 2"}

    def test_lifecycle_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inferred_rules.json"
            store = InferredRuleStore(path)

            ir = InferredRule(rule=Rule(id="r1", name="Test", steps=[]))
            ir.promote_to(RuleLifecycle.EXECUTABLE)
            store.save(ir)

            loaded = store.load_all()
            assert loaded[0].lifecycle == RuleLifecycle.EXECUTABLE

    def test_persistence_file_created(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inferred_rules.json"
            store = InferredRuleStore(path)

            ir = InferredRule(rule=Rule(id="r1", name="Test", steps=[]))
            store.save(ir)

            assert path.is_file()
            content = path.read_text(encoding="utf-8")
            assert "Test" in content
            assert "INFERRED" in content


# ── StepInfo ──────────────────────────────────────────────────────

class TestStepInfo:
    def test_unknown_step_fallback_label(self) -> None:
        step = RuleStep(type="future_ai_feature", parameters={"ai": "yes"})
        info = StepInfo.from_step(step, 0)
        assert info.label == "future_ai_feature"
        assert info.step_type == "future_ai_feature"
