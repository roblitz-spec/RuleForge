"""WP-1: Stable RuleStep Identity — identity creation, legacy migration, clone identity, JSON round-trip."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from uuid import UUID

from models.rule import Rule
from models.rule_step import RuleStep
from storage.json_storage import JsonStorage


class TestRuleStepIdentity:
    """WP-1: RuleStep.id is a stable UUID assigned at construction."""

    def test_new_step_has_uuid(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        assert step.id
        UUID(step.id)  # does not raise

    def test_new_step_uuid_is_unique(self) -> None:
        ids = {RuleStep(type="replace").id for _ in range(100)}
        assert len(ids) == 100

    def test_explicit_id_accepted(self) -> None:
        step = RuleStep(type="replace", id="explicit-id-123")
        assert step.id == "explicit-id-123"

    def test_id_field_in_dataclass(self) -> None:
        step = RuleStep(type="case", parameters={"mode": "upper"})
        assert hasattr(step, "id")
        assert isinstance(step.id, str)
        assert len(step.id) == 36  # standard UUID string


class TestLegacyMigration:
    """WP-1: Legacy JSON without step.id auto-generates UUID on load."""

    def test_legacy_json_without_id_gets_uuid(self) -> None:
        legacy_json = {
            "version": 1,
            "rules": [
                {
                    "id": "r1",
                    "name": "Test",
                    "description": "",
                    "pinned": False,
                    "steps": [
                        {"type": "replace", "parameters": {"from": "a", "to": "b"}},
                        {"type": "case", "parameters": {"mode": "upper"}},
                    ],
                }
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(legacy_json, f, ensure_ascii=False)
            tmp_path = Path(f.name)

        try:
            rules = JsonStorage.load_rules(tmp_path)
            assert len(rules) == 1
            assert len(rules[0].steps) == 2
            for step in rules[0].steps:
                assert step.id
                UUID(step.id)  # valid UUID
                assert len(step.id) == 36
        finally:
            tmp_path.unlink()

    def test_legacy_json_ids_are_unique(self) -> None:
        legacy_json = {
            "version": 1,
            "rules": [
                {
                    "id": "r1",
                    "name": "Test",
                    "description": "",
                    "pinned": False,
                    "steps": [
                        {"type": "replace", "parameters": {"from": "a", "to": "b"}},
                        {"type": "replace", "parameters": {"from": "c", "to": "d"}},
                        {"type": "replace", "parameters": {"from": "e", "to": "f"}},
                    ],
                }
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(legacy_json, f, ensure_ascii=False)
            tmp_path = Path(f.name)

        try:
            rules = JsonStorage.load_rules(tmp_path)
            ids = [s.id for s in rules[0].steps]
            assert len(ids) == len(set(ids))  # all unique
        finally:
            tmp_path.unlink()


class TestCloneIdentity:
    """WP-1: Cloned/copied RuleStep must have a new UUID."""

    def test_clone_by_construction_gets_new_uuid(self) -> None:
        original = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        clone = RuleStep(
            type=original.type,
            parameters=dict(original.parameters),
        )
        assert clone.id != original.id
        UUID(clone.id)
        UUID(original.id)

    def test_clone_preserves_type_and_params(self) -> None:
        original = RuleStep(
            type="regex_replace",
            parameters={"pattern": r"\d+", "replacement": ""},
        )
        clone = RuleStep(
            type=original.type,
            parameters=dict(original.parameters),
        )
        assert clone.type == original.type
        assert clone.parameters == original.parameters
        assert clone.id != original.id


class TestJsonRoundTrip:
    """WP-1: JSON save → load preserves step.id."""

    def test_round_trip_preserves_ids(self) -> None:
        rule = Rule(
            id="r-test",
            name="RoundTrip",
            steps=[
                RuleStep(type="replace", parameters={"from": "x", "to": "y"}),
                RuleStep(type="case", parameters={"mode": "upper"}),
            ],
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            tmp_path = Path(f.name)

        try:
            JsonStorage.save_rules(tmp_path, [rule])
            loaded = JsonStorage.load_rules(tmp_path)
            assert len(loaded) == 1
            assert len(loaded[0].steps) == 2
            assert loaded[0].steps[0].id == rule.steps[0].id
            assert loaded[0].steps[1].id == rule.steps[1].id
            assert loaded[0].steps[0].type == "replace"
            assert loaded[0].steps[1].type == "case"
        finally:
            tmp_path.unlink()

    def test_round_trip_legacy_to_new_format(self) -> None:
        """Load legacy (no id), save (with id), reload — ids are stable after first save."""
        legacy_json = {
            "version": 1,
            "rules": [
                {
                    "id": "r1",
                    "name": "Test",
                    "description": "",
                    "pinned": False,
                    "steps": [
                        {"type": "replace", "parameters": {"from": "a", "to": "b"}},
                    ],
                }
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(legacy_json, f, ensure_ascii=False)
            tmp_path = Path(f.name)

        try:
            # First load: auto-generates UUID
            rules_v1 = JsonStorage.load_rules(tmp_path)
            step_id = rules_v1[0].steps[0].id
            assert step_id

            # Save with id
            JsonStorage.save_rules(tmp_path, rules_v1)

            # Second load: id is stable
            rules_v2 = JsonStorage.load_rules(tmp_path)
            assert rules_v2[0].steps[0].id == step_id
        finally:
            tmp_path.unlink()

    def test_saved_json_contains_id_field(self) -> None:
        rule = Rule(
            id="r-test",
            name="WithID",
            steps=[RuleStep(type="replace", parameters={"from": "x", "to": "y"})],
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            tmp_path = Path(f.name)

        try:
            JsonStorage.save_rules(tmp_path, [rule])
            raw = json.loads(tmp_path.read_text(encoding="utf-8"))
            step_data = raw["rules"][0]["steps"][0]
            assert "id" in step_data
            UUID(step_data["id"])
        finally:
            tmp_path.unlink()
