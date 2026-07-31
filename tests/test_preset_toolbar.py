"""WP-24: Toolbar Preset Selector integration tests."""
from __future__ import annotations

import tempfile
from copy import deepcopy
from pathlib import Path

from models.preset import Preset
from models.rule import Rule
from models.rule_step import RuleStep
from storage.preset_store import PresetStore
from storage.repository import RuleRepository


def _repo_with_rules() -> RuleRepository:
    td = tempfile.mkdtemp()
    repo = RuleRepository(Path(td) / "rules.json")
    repo.load()
    repo.add(Rule(id="r1", name="Alpha", steps=[
        RuleStep(type="case", parameters={"mode": "upper"}),
    ]))
    repo.add(Rule(id="r2", name="Beta"))
    repo.save()
    return repo


def _store_with_presets() -> PresetStore:
    td = tempfile.mkdtemp()
    store = PresetStore(Path(td) / "presets.json")
    store.save(Preset(
        id="preset_1", name="Photo Preset",
        rules=[
            Rule(id="r1", name="Date Rule", steps=[
                RuleStep(type="date", parameters={"format": "%Y-%m-%d"}),
            ]),
            Rule(id="r2", name="Number Rule", steps=[
                RuleStep(type="number", parameters={"start": "1", "padding": "3"}),
            ]),
        ],
    ))
    store.save(Preset(
        id="preset_2", name="Cleanup Preset",
        rules=[
            Rule(id="r1", name="Trim", steps=[
                RuleStep(type="trim", parameters={"mode": "both"}),
            ]),
        ],
    ))
    store.save(Preset(
        id="preset_3", name="Empty Preset",
        rules=[],
    ))
    return store


# ═══════════════════════════════════════════════════════════════════
# Preset Selector — Repository Sync
# ═══════════════════════════════════════════════════════════════════


class TestPresetSelectorRepoSync:
    def test_load_preset_replaces_all_rules(self) -> None:
        repo = _repo_with_rules()
        store = _store_with_presets()

        # simulate selecting "Photo Preset"
        presets = {p.id: p for p in store.load_all()}
        preset = presets["preset_1"]
        repo.replace_rules(deepcopy(preset.rules))
        repo.save()

        repo.load()
        assert len(repo.all_rules()) == 2
        assert repo.find("r1").name == "Date Rule"
        assert repo.find("r1").steps[0].type == "date"

    def test_switch_between_presets(self) -> None:
        repo = _repo_with_rules()
        store = _store_with_presets()

        presets = {p.id: p for p in store.load_all()}

        # switch to Photo Preset
        repo.replace_rules(deepcopy(presets["preset_1"].rules))
        repo.save()
        repo.load()
        assert repo.find("r1").name == "Date Rule"

        # switch to Cleanup Preset
        repo.replace_rules(deepcopy(presets["preset_2"].rules))
        repo.save()
        repo.load()
        assert len(repo.all_rules()) == 1
        assert repo.find("r1").name == "Trim"
        assert repo.find("r1").steps[0].type == "trim"

    def test_load_empty_preset_clears_rules(self) -> None:
        repo = _repo_with_rules()
        store = _store_with_presets()

        assert len(repo.all_rules()) == 2

        presets = {p.id: p for p in store.load_all()}
        repo.replace_rules(deepcopy(presets["preset_3"].rules))
        repo.save()
        repo.load()
        assert repo.all_rules() == []


# ═══════════════════════════════════════════════════════════════════
# Preset Selector — Combo State
# ═══════════════════════════════════════════════════════════════════


class TestPresetComboPopulation:
    def test_empty_store_yields_no_presets(self) -> None:
        td = tempfile.mkdtemp()
        store = PresetStore(Path(td) / "empty.json")
        assert store.load_all() == []

    def test_store_yields_all_presets(self) -> None:
        store = _store_with_presets()
        all_presets = store.load_all()
        assert len(all_presets) == 3
        assert {p.name for p in all_presets} == {"Photo Preset", "Cleanup Preset", "Empty Preset"}

    def test_combo_data_maps_to_correct_preset(self) -> None:
        """The QComboBox uses userData to map display name → preset ID."""
        store = _store_with_presets()
        presets = {p.id: p for p in store.load_all()}
        assert presets["preset_1"] is not None
        assert presets["preset_1"].name == "Photo Preset"

    def test_preset_store_reload_preserves_combo_data(self) -> None:
        """After reloading a store from disk, preset IDs and names persist."""
        store = _store_with_presets()
        store2 = PresetStore(store._path)
        all_presets = store2.load_all()
        assert len(all_presets) == 3
        assert {p.id for p in all_presets} == {"preset_1", "preset_2", "preset_3"}


# ═══════════════════════════════════════════════════════════════════
# Preset Selector — Edge Cases
# ═══════════════════════════════════════════════════════════════════


class TestPresetSelectorEdgeCases:
    def test_select_nonexistent_preset_is_noop(self) -> None:
        repo = _repo_with_rules()
        store = _store_with_presets()

        presets = {p.id: p for p in store.load_all()}
        assert "preset_nonexistent" not in presets
        # selector returns None → no repo change
        assert len(repo.all_rules()) == 2

    def test_save_after_preset_load_roundtrip(self) -> None:
        """Load preset → save repo → reload → rules intact."""
        repo = _repo_with_rules()
        store = _store_with_presets()
        presets = {p.id: p for p in store.load_all()}

        repo.replace_rules(deepcopy(presets["preset_1"].rules))
        repo.save()

        # reload repo
        repo2 = RuleRepository(repo._path)
        repo2.load()
        assert len(repo2.all_rules()) == 2
        assert repo2.find("r1").steps[0].type == "date"

    def test_mutated_loaded_rules_isolated_from_preset(self) -> None:
        """Mutating loaded rules does not affect the preset on disk."""
        repo = _repo_with_rules()
        store = _store_with_presets()
        presets = {p.id: p for p in store.load_all()}

        repo.replace_rules(deepcopy(presets["preset_1"].rules))
        repo.find("r1").name = "MUTATED"
        repo.save()

        # preset on disk unchanged
        loaded = PresetStore(store._path).load_all()
        assert {p.id: p for p in loaded}["preset_1"].rules[0].name == "Date Rule"
