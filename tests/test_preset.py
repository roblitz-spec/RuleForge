"""WP-22: PresetStore CRUD tests."""
from __future__ import annotations

import tempfile
from copy import deepcopy
from pathlib import Path

from models.preset import Preset
from models.rule import Rule
from models.rule_step import RuleStep
from storage.preset_store import PresetStore


def _make_store() -> PresetStore:
    td = tempfile.mkdtemp()
    return PresetStore(Path(td) / "presets.json")


def _make_preset(name: str = "Test Preset", id_: str = "preset_1") -> Preset:
    return Preset(
        id=id_,
        name=name,
        description="A test preset",
        rules=[
            Rule(id="r1", name="Rule A", steps=[
                RuleStep(type="replace", parameters={"from": "a", "to": "b"}),
            ]),
        ],
    )


# ═══════════════════════════════════════════════════════════════════
# Preset Dataclass
# ═══════════════════════════════════════════════════════════════════


class TestPresetDataclass:
    def test_defaults(self) -> None:
        p = Preset(id="p1", name="Test")
        assert p.description == ""
        assert p.rules == []
        assert p.version == 1

    def test_with_rules(self) -> None:
        rules = [Rule(id="r1", name="R1")]
        p = Preset(id="p1", name="Test", rules=rules)
        assert len(p.rules) == 1
        assert p.rules[0].id == "r1"


# ═══════════════════════════════════════════════════════════════════
# PresetStore — CRUD
# ═══════════════════════════════════════════════════════════════════


class TestPresetStoreCRUD:
    def test_load_all_empty_when_no_file(self) -> None:
        s = _make_store()
        assert s.load_all() == []

    def test_save_and_load_single(self) -> None:
        s = _make_store()
        preset = _make_preset()
        s.save(preset)

        all_presets = s.load_all()
        assert len(all_presets) == 1
        assert all_presets[0].name == "Test Preset"

    def test_save_multiple_distinct(self) -> None:
        s = _make_store()
        s.save(_make_preset("A", "preset_1"))
        s.save(_make_preset("B", "preset_2"))

        all_presets = s.load_all()
        assert len(all_presets) == 2
        assert {p.name for p in all_presets} == {"A", "B"}

    def test_save_overwrites_existing_by_id(self) -> None:
        s = _make_store()
        s.save(_make_preset("Original", "preset_1"))
        s.save(_make_preset("Updated", "preset_1"))

        all_presets = s.load_all()
        assert len(all_presets) == 1
        assert all_presets[0].name == "Updated"

    def test_delete_removes_preset(self) -> None:
        s = _make_store()
        s.save(_make_preset("A", "preset_1"))
        s.save(_make_preset("B", "preset_2"))

        s.delete("preset_1")
        all_presets = s.load_all()
        assert len(all_presets) == 1
        assert all_presets[0].id == "preset_2"

    def test_delete_nonexistent_is_noop(self) -> None:
        s = _make_store()
        s.save(_make_preset())
        s.delete("preset_nonexistent")
        assert len(s.load_all()) == 1

    def test_rename_updates_name(self) -> None:
        s = _make_store()
        s.save(_make_preset("Old Name"))
        s.rename("preset_1", "New Name")

        assert s.load_all()[0].name == "New Name"

    def test_rename_nonexistent_is_noop(self) -> None:
        s = _make_store()
        s.save(_make_preset())
        s.rename("preset_nonexistent", "Whatever")
        assert s.load_all()[0].name == "Test Preset"

    def test__next_id_first(self) -> None:
        s = _make_store()
        assert s._next_id() == "preset_1"

    def test__next_id_with_existing(self) -> None:
        s = _make_store()
        s.save(_make_preset(id_="preset_1"))
        s.save(_make_preset("B", id_="preset_3"))
        assert s._next_id() == "preset_2"


# ═══════════════════════════════════════════════════════════════════
# PresetStore — Persistence Round-trip
# ═══════════════════════════════════════════════════════════════════


class TestPresetStorePersistence:
    def test_save_reload_preserves_rules(self) -> None:
        s1 = _make_store()
        preset = Preset(
            id="preset_1",
            name="Photo Rename",
            description="Standard photo workflow",
            rules=[
                Rule(id="r1", name="Add Date", steps=[
                    RuleStep(type="date", parameters={"format": "%Y-%m-%d"}),
                ]),
                Rule(id="r2", name="Number", steps=[
                    RuleStep(type="number", parameters={"start": "1", "padding": "3"}),
                ]),
            ],
        )
        s1.save(preset)

        # reload from same file
        s2 = PresetStore(s1._path)
        loaded = s2.load_all()
        assert len(loaded) == 1
        p = loaded[0]
        assert p.id == "preset_1"
        assert p.name == "Photo Rename"
        assert p.description == "Standard photo workflow"
        assert len(p.rules) == 2
        assert p.rules[0].id == "r1"
        assert p.rules[0].name == "Add Date"
        assert p.rules[0].steps[0].type == "date"
        assert p.rules[0].steps[0].parameters["format"] == "%Y-%m-%d"
        assert p.rules[1].id == "r2"
        assert p.rules[1].steps[0].type == "number"
        assert p.rules[1].steps[0].parameters["start"] == "1"

    def test_save_reload_empty_preset(self) -> None:
        s1 = _make_store()
        s1.save(Preset(id="p1", name="Empty"))
        s2 = PresetStore(s1._path)
        loaded = s2.load_all()
        assert len(loaded) == 1
        assert loaded[0].rules == []

    def test_save_reload_multiple_presets(self) -> None:
        s1 = _make_store()
        s1.save(_make_preset("A", "preset_1"))
        s1.save(_make_preset("B", "preset_2"))
        s1.save(_make_preset("C", "preset_3"))

        s2 = PresetStore(s1._path)
        loaded = s2.load_all()
        assert len(loaded) == 3
        assert {p.name for p in loaded} == {"A", "B", "C"}

    def test_delete_persists_across_reload(self) -> None:
        s1 = _make_store()
        s1.save(_make_preset("A", "preset_1"))
        s1.save(_make_preset("B", "preset_2"))
        s1.delete("preset_1")

        s2 = PresetStore(s1._path)
        loaded = s2.load_all()
        assert len(loaded) == 1
        assert loaded[0].id == "preset_2"

    def test_rename_persists_across_reload(self) -> None:
        s1 = _make_store()
        s1.save(_make_preset("Old", "preset_1"))
        s1.rename("preset_1", "Renamed")

        s2 = PresetStore(s1._path)
        loaded = s2.load_all()
        assert loaded[0].name == "Renamed"

    def test_missing_file_loads_empty(self) -> None:
        td = tempfile.mkdtemp()
        s = PresetStore(Path(td) / "nonexistent.json")
        assert s.load_all() == []


# ═══════════════════════════════════════════════════════════════════
# PresetStore — Edge Cases
# ═══════════════════════════════════════════════════════════════════


class TestPresetStoreEdgeCases:
    def test_preset_with_no_steps(self) -> None:
        s = _make_store()
        preset = Preset(
            id="p1", name="No Steps",
            rules=[Rule(id="r1", name="Empty Rule")],
        )
        s.save(preset)

        s2 = PresetStore(s._path)
        loaded = s2.load_all()
        assert loaded[0].rules[0].steps == []

    def test_preset_rules_are_independent(self) -> None:
        """Preset rules must be deep copies — no shared references."""
        s = _make_store()
        presets = [
            Preset(id="p1", name="A", rules=[Rule(id="r1", name="Same Rule")]),
            Preset(id="p2", name="B", rules=[Rule(id="r1", name="Same Rule")]),
        ]
        for p in presets:
            s.save(p)

        loaded = s.load_all()
        loaded[0].rules[0].name = "Mutated"

        s2 = PresetStore(s._path)
        reloaded = s2.load_all()
        assert reloaded[0].rules[0].name == "Same Rule"

    def test_delete_all_presets_is_empty(self) -> None:
        s = _make_store()
        s.save(_make_preset("A", "preset_1"))
        s.save(_make_preset("B", "preset_2"))
        s.delete("preset_1")
        s.delete("preset_2")

        s2 = PresetStore(s._path)
        assert s2.load_all() == []

    def test_save_then_delete_then_reload(self) -> None:
        s1 = _make_store()
        s1.save(_make_preset("A", "preset_1"))
        s1.delete("preset_1")

        s2 = PresetStore(s1._path)
        assert s2.load_all() == []
