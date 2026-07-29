from __future__ import annotations

import tempfile
from pathlib import Path

from models.rule import Rule
from models.rule_step import RuleStep
from storage.json_storage import JsonStorage
from storage.repository import RuleRepository


class TestRuleEditor:
    """RuleStep 编辑 & 持久化测试。"""

    def test_rule_with_steps_persists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "rules.json"
            repo = RuleRepository(p)
            repo.load()

            rule = Rule(id="r1", name="测试", steps=[
                RuleStep(type="replace", parameters={"from": "_", "to": " "}),
                RuleStep(type="add_prefix", parameters={"text": "[HD]"}),
            ])
            repo.add(rule)
            repo.save()

            repo2 = RuleRepository(p)
            repo2.load()
            r = repo2.find("r1")
            assert r is not None
            assert len(r.steps) == 2
            assert r.steps[0].type == "replace"
            assert r.steps[0].parameters["from"] == "_"
            assert r.steps[1].type == "add_prefix"
            assert r.steps[1].parameters["text"] == "[HD]"

    def test_step_order_persists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "rules.json"
            repo = RuleRepository(p)
            repo.load()

            rule = Rule(id="r1", name="顺序", steps=[
                RuleStep(type="add_prefix", parameters={"text": "A"}),
                RuleStep(type="replace", parameters={"from": "x", "to": "y"}),
            ])
            repo.add(rule)
            repo.save()

            repo2 = RuleRepository(p)
            repo2.load()
            r = repo2.find("r1")
            assert r.steps[0].type == "add_prefix"
            assert r.steps[1].type == "replace"

    def test_json_roundtrip_with_steps(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "rules.json"
            rules = [
                Rule(id="r1", name="R1", steps=[
                    RuleStep(type="replace", parameters={"from": "_", "to": " "}),
                ]),
            ]
            JsonStorage.save_rules(p, rules)
            loaded = JsonStorage.load_rules(p)
            assert len(loaded) == 1
            assert len(loaded[0].steps) == 1
            assert loaded[0].steps[0].parameters["from"] == "_"


# ═══════════════════════════════════════════════════════════════════
# WP-16: Rule Duplication
# ═══════════════════════════════════════════════════════════════════

class TestRuleDuplicate:
    """Unit tests for RuleRepository.duplicate()."""

    # ── 基本行为 ──

    def test_duplicate_is_deep_copy(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="测试", description="desc", steps=[
                RuleStep(type="replace", parameters={"from": "_", "to": " "}),
            ])
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup is not original
            assert dup.steps is not original.steps
            assert dup.steps[0] is not original.steps[0]

    def test_duplicate_new_unique_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="原始")
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup.id != original.id
            assert dup.id.startswith("rule_")

    def test_duplicate_id_no_collision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            r1 = Rule(id="rule_1", name="R1")
            r2 = Rule(id="rule_2", name="R2")
            repo.add(r1)
            repo.add(r2)
            dup = repo.duplicate(r1)
            assert dup.id == "rule_3"

    def test_duplicate_name_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="图片重命名")
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup.name == "图片重命名 (副本)"

    def test_duplicate_pinned_not_inherited(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Test", pinned=True)
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup.pinned is False

    # ── 内容保留 ──

    def test_duplicate_preserves_steps(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Test", steps=[
                RuleStep(type="replace", parameters={"from": "a", "to": "b"}),
                RuleStep(type="add_prefix", parameters={"text": "IMG_"}),
                RuleStep(type="case", parameters={"mode": "upper"}),
            ])
            repo.add(original)
            dup = repo.duplicate(original)
            assert len(dup.steps) == 3
            assert dup.steps[0].type == "replace"
            assert dup.steps[0].parameters == {"from": "a", "to": "b"}
            assert dup.steps[1].type == "add_prefix"
            assert dup.steps[1].parameters == {"text": "IMG_"}
            assert dup.steps[2].type == "case"
            assert dup.steps[2].parameters == {"mode": "upper"}

    def test_duplicate_preserves_description(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Test", description="替换下划线为空格")
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup.description == "替换下划线为空格"

    def test_duplicate_empty_steps(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Empty", steps=[])
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup.steps == []

    # ── 隔离性 ──

    def test_duplicate_mutation_isolation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Test", steps=[
                RuleStep(type="replace", parameters={"from": "a", "to": "b"}),
            ])
            repo.add(original)
            dup = repo.duplicate(original)
            # 修改副本
            dup.name = "Modified"
            dup.steps[0].parameters["from"] = "x"
            # 原始不受影响
            assert original.name == "Test"
            assert original.steps[0].parameters["from"] == "a"

    def test_duplicate_original_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Test", steps=[
                RuleStep(type="trim", parameters={"mode": "both"}),
                RuleStep(type="number", parameters={"start": "1", "step": "1", "padding": "2"}),
            ], pinned=True, description="原始描述")
            repo.add(original)
            dup = repo.duplicate(original)
            # 原始完全不变
            assert original.id == "r1"
            assert original.name == "Test"
            assert original.description == "原始描述"
            assert original.pinned is True
            assert len(original.steps) == 2
            # 副本独立
            assert dup.id != "r1"
            assert dup.pinned is False

    # ── 持久化 ──

    def test_duplicate_save_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "rules.json"
            repo = RuleRepository(p)
            repo.load()
            original = Rule(id="r1", name="Test", steps=[
                RuleStep(type="replace", parameters={"from": "_", "to": " "}),
            ])
            repo.add(original)
            dup = repo.duplicate(original)
            repo.save()

            repo2 = RuleRepository(p)
            repo2.load()
            found = repo2.find(dup.id)
            assert found is not None
            assert found.name == "Test (副本)"
            assert len(found.steps) == 1
            assert found.steps[0].type == "replace"
            assert found.steps[0].parameters["from"] == "_"

    def test_duplicate_repository_contains_both(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Original")
            repo.add(original)
            dup = repo.duplicate(original)
            assert len(repo.all_rules()) == 2
            assert repo.find("r1") is not None
            assert repo.find(dup.id) is not None

    # ── 所有 step type ──

    def test_duplicate_all_step_types(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="All Types", steps=[
                RuleStep(type="replace", parameters={"from": "a", "to": "b"}),
                RuleStep(type="remove_text", parameters={"text": "x"}),
                RuleStep(type="regex_replace", parameters={"pattern": r"\d", "replacement": ""}),
                RuleStep(type="case", parameters={"mode": "upper"}),
                RuleStep(type="trim", parameters={"mode": "both"}),
                RuleStep(type="number", parameters={"start": "1", "step": "1", "padding": "2"}),
                RuleStep(type="insert", parameters={"text": "X", "at_index": "0"}),
                RuleStep(type="date", parameters={"source": "modified", "format": "%Y-%m-%d"}),
                RuleStep(type="add_prefix", parameters={"text": "IMG_"}),
                RuleStep(type="add_suffix", parameters={"text": "_final"}),
            ])
            repo.add(original)
            dup = repo.duplicate(original)
            assert len(dup.steps) == 10
            for i, s in enumerate(dup.steps):
                assert s.type == original.steps[i].type
                assert s.parameters == original.steps[i].parameters
                assert s is not original.steps[i]


# ═══════════════════════════════════════════════════════════════════
# WP-17: Rule Duplication UI Integration
# ═══════════════════════════════════════════════════════════════════

class TestRuleDuplicateIntegration:
    """Integration tests for the WP-17 UI flow (Repository layer, no Qt)."""

    def test_duplicate_save_reload_flow(self) -> None:
        """Simulates the full WP-17 dialog flow: duplicate → save → reload."""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "rules.json"
            repo = RuleRepository(p)
            repo.load()
            rule = Rule(id="r1", name="原始", steps=[
                RuleStep(type="replace", parameters={"from": "_", "to": " "}),
            ])
            repo.add(rule)
            repo.save()

            # WP-17 dialog flow
            dup = repo.duplicate(rule)
            repo.save()

            # Reload: verify both rules persist
            repo2 = RuleRepository(p)
            repo2.load()
            assert len(repo2.all_rules()) == 2
            assert repo2.find("r1") is not None
            assert repo2.find(dup.id) is not None

    def test_duplicate_selectable_after_refresh(self) -> None:
        """After duplicate+save, all_rules() returns both (mimics _refresh_rule_list)."""
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            rule = Rule(id="r1", name="Original")
            repo.add(rule)
            dup = repo.duplicate(rule)
            repo.save()

            rules = repo.all_rules()
            assert len(rules) == 2
            ids = {r.id for r in rules}
            assert "r1" in ids
            assert dup.id in ids

    def test_duplicate_preserves_original_in_list(self) -> None:
        """Original rule remains unchanged and visible after duplicate."""
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Original", pinned=True, steps=[
                RuleStep(type="case", parameters={"mode": "upper"}),
            ])
            repo.add(original)
            dup = repo.duplicate(original)
            repo.save()

            found = repo.find("r1")
            assert found is not None
            assert found.name == "Original"
            assert found.pinned is True
            assert len(found.steps) == 1

    def test_duplicate_returns_new_rule_for_selection(self) -> None:
        """duplicate() returns the new rule (mimics _select_rule_in_list(dup.id))."""
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            rule = Rule(id="r1", name="Test")
            repo.add(rule)
            dup = repo.duplicate(rule)
            # Verify the returned rule can be found by its ID
            found = repo.find(dup.id)
            assert found is not None
            assert found is dup

    def test_duplicate_twice_creates_unique_rules(self) -> None:
        """Duplicating twice creates two distinct copies (tests repeated context menu use)."""
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            rule = Rule(id="r1", name="Test")
            repo.add(rule)
            dup1 = repo.duplicate(rule)
            dup2 = repo.duplicate(rule)
            repo.save()
            assert dup1.id != dup2.id
            assert len(repo.all_rules()) == 3
            ids = {r.id for r in repo.all_rules()}
            assert len(ids) == 3


# ═══════════════════════════════════════════════════════════════════
# WP-18: Edge Case Verification & Hardening
# ═══════════════════════════════════════════════════════════════════

class TestRuleDuplicateEdgeCases:
    """Edge case and boundary condition tests for WP-16/WP-17."""

    # ── 复杂参数 ──

    def test_complex_unicode_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Unicode", steps=[
                RuleStep(type="replace", parameters={"from": "αβγ", "to": "ΔΕΦ"}),
                RuleStep(type="regex_replace", parameters={
                    "pattern": r"[ο-ωァ-ン]", "replacement": "λ",
                }),
            ])
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup.steps[0].parameters["from"] == "αβγ"
            assert dup.steps[0].parameters["to"] == "ΔΕΦ"
            assert dup.steps[1].parameters["pattern"] == r"[ο-ωァ-ン]"

    def test_special_chars_in_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Special", steps=[
                RuleStep(type="replace", parameters={"from": "\n\t", "to": "\\"}),
                RuleStep(type="add_prefix", parameters={"text": "IMG_001_"}),
            ])
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup.steps[0].parameters["from"] == "\n\t"
            assert dup.steps[0].parameters["to"] == "\\"

    def test_name_with_parentheses(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="图片 (高清)")
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup.name == "图片 (高清) (副本)"

    def test_name_already_has_copy_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="图片 (副本)")
            repo.add(original)
            dup = repo.duplicate(original)
            assert dup.name == "图片 (副本) (副本)"

    # ── 多次复制 ──

    def test_ten_duplications_unique_ids(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Test")
            repo.add(original)
            ids = {"r1"}
            for _ in range(10):
                dup = repo.duplicate(original)
                assert dup.id not in ids
                ids.add(dup.id)
            assert len(ids) == 11
            assert len(repo.all_rules()) == 11

    def test_duplicate_of_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            original = Rule(id="r1", name="Original")
            repo.add(original)
            dup1 = repo.duplicate(original)
            dup2 = repo.duplicate(dup1)  # duplicate of duplicate
            assert dup2.id != dup1.id
            assert dup2.id != original.id
            assert dup2.name == "Original (副本) (副本)"
            assert len(repo.all_rules()) == 3

    # ── 持久化工作流 ──

    def test_save_reload_then_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "rules.json"
            repo = RuleRepository(p)
            repo.load()
            repo.add(Rule(id="r1", name="Test"))
            repo.save()

            # Reload
            repo2 = RuleRepository(p)
            repo2.load()
            rule = repo2.find("r1")
            assert rule is not None
            dup = repo2.duplicate(rule)
            repo2.save()

            # Verify persistence
            repo3 = RuleRepository(p)
            repo3.load()
            assert repo3.find("r1") is not None
            assert repo3.find(dup.id) is not None

    def test_mutation_isolation_after_persistence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "rules.json"
            repo = RuleRepository(p)
            repo.load()
            original = Rule(id="r1", name="Test", steps=[
                RuleStep(type="replace", parameters={"from": "_", "to": " "}),
            ])
            repo.add(original)
            dup = repo.duplicate(original)
            repo.save()

            # Reload and mutate
            repo2 = RuleRepository(p)
            repo2.load()
            orig2 = repo2.find("r1")
            dup2 = repo2.find(dup.id)
            assert orig2 is not None
            assert dup2 is not None
            # Mutate duplicate
            dup2.name = "Modified"
            dup2.steps[0].parameters["from"] = "x"
            # Original unchanged
            assert orig2.name == "Test"
            assert orig2.steps[0].parameters["from"] == "_"

    # ── 大型仓库 ID 碰撞 ──

    def test_large_repository_id_no_collision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            # Pre-populate with 50 rules
            for i in range(1, 51):
                repo.add(Rule(id=f"rule_{i}", name=f"R{i}"))
            rule = repo.find("rule_1")
            assert rule is not None
            dup = repo.duplicate(rule)
            assert dup.id == "rule_51"
            assert len(repo.all_rules()) == 51

    def test_gapped_ids_next_available(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            repo.add(Rule(id="rule_1", name="R1"))
            repo.add(Rule(id="rule_5", name="R5"))
            repo.add(Rule(id="rule_9", name="R9"))
            dup = repo.duplicate(repo.find("rule_1"))
            assert dup.id == "rule_2"  # first gap


# ═══════════════════════════════════════════════════════════════════
# WP-19: ID Generation Consolidation
# ═══════════════════════════════════════════════════════════════════

class TestIDGenerationConsolidation:
    """Tests verifying ID generation is unified in Repository."""

    def test_generate_unique_id_public(self) -> None:
        """generate_unique_id() is an accessible public method on Repository."""
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            uid = repo.generate_unique_id()
            assert uid.startswith("rule_")

    def test_add_then_generate_does_not_collide(self) -> None:
        """Adding a rule then calling generate_unique_id produces a non-conflicting ID."""
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            repo.add(Rule(id="rule_1", name="R1"))
            uid = repo.generate_unique_id()
            assert uid == "rule_2"

    def test_duplicate_uses_repository_method(self) -> None:
        """duplicate() calls self.generate_unique_id() — the Repository's own method."""
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            repo.add(Rule(id="rule_1", name="Test"))
            dup = repo.duplicate(repo.find("rule_1"))
            assert dup.id == "rule_2"

    def test_consolidation_preserves_id_format(self) -> None:
        """Both add path and duplicate path produce rule_N format IDs."""
        with tempfile.TemporaryDirectory() as td:
            repo = RuleRepository(Path(td) / "rules.json")
            repo.load()
            add_id = repo.generate_unique_id()
            assert add_id == "rule_1"
            repo.add(Rule(id=add_id, name="Test"))
            dup = repo.duplicate(repo.find(add_id))
            assert dup.id == "rule_2"
            assert add_id.startswith("rule_")
            assert dup.id.startswith("rule_")
