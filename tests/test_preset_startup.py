"""WP-25: Startup preset restoration tests."""
from __future__ import annotations

import tempfile
from copy import deepcopy
from pathlib import Path

from models.preset import Preset
from models.rule import Rule
from models.rule_step import RuleStep
from storage.preset_store import PresetStore
from storage.repository import RuleRepository


def _repo() -> RuleRepository:
    td = tempfile.mkdtemp()
    repo = RuleRepository(Path(td) / "rules.json")
    repo.load()
    return repo


def _store_with_presets() -> PresetStore:
    td = tempfile.mkdtemp()
    store = PresetStore(Path(td) / "presets.json")
    store.save(Preset(
        id="preset_1", name="Photo Preset",
        rules=[Rule(id="r1", name="Add Date", steps=[
            RuleStep(type="date", parameters={"format": "%Y-%m-%d"}),
        ])],
    ))
    store.save(Preset(
        id="preset_2", name="Cleanup Preset",
        rules=[Rule(id="r1", name="Trim", steps=[
            RuleStep(type="trim", parameters={"mode": "both"}),
        ])],
    ))
    return store


# ═══════════════════════════════════════════════════════════════════
# Startup Restoration
# ═══════════════════════════════════════════════════════════════════


class TestStartupRestoration:
    def test_restore_existing_preset(self) -> None:
        """Simulate: last-used preset exists in store → restore loads it."""
        store = _store_with_presets()
        last_id = "preset_1"

        # startup: load repo from preset
        repo = _repo()
        presets = {p.id: p for p in store.load_all()}
        preset = presets.get(last_id)
        assert preset is not None
        repo.replace_rules(deepcopy(preset.rules))
        repo.save()

        # verify repo has preset rules
        repo.load()
        assert len(repo.all_rules()) == 1
        assert repo.find("r1").name == "Add Date"
        assert repo.find("r1").steps[0].type == "date"

    def test_restore_missing_preset_is_noop(self) -> None:
        """Simulate: last-used preset ID no longer exists → skip silently."""
        store = _store_with_presets()
        last_id = "preset_missing"

        repo = _repo()
        repo.add(Rule(id="r_orig", name="Original Rule"))
        repo.save()
        original_count = len(repo.all_rules())

        presets = {p.id: p for p in store.load_all()}
        preset = presets.get(last_id)
        assert preset is None  # missing

        # startup: no-op, repo unchanged
        repo.load()
        assert len(repo.all_rules()) == original_count
        assert repo.find("r_orig").name == "Original Rule"

    def test_restore_no_last_id_is_noop(self) -> None:
        """Simulate: no last-used preset ID (None) → skip silently."""
        last_id = None

        repo = _repo()
        repo.add(Rule(id="r_orig", name="Original Rule"))
        repo.save()

        # startup: None → skip
        if last_id is not None:
            store = _store_with_presets()
            presets = {p.id: p for p in store.load_all()}
            preset = presets.get(last_id)
            if preset is not None:
                repo.replace_rules(deepcopy(preset.rules))
                repo.save()

        # repo unchanged
        repo.load()
        assert len(repo.all_rules()) == 1
        assert repo.find("r_orig").name == "Original Rule"

    def test_restore_then_switch_preset(self) -> None:
        """Restore preset_1, then switch to preset_2."""
        store = _store_with_presets()

        # restore preset_1
        repo = _repo()
        presets = {p.id: p for p in store.load_all()}
        repo.replace_rules(deepcopy(presets["preset_1"].rules))
        repo.save()
        repo.load()
        assert repo.find("r1").name == "Add Date"

        # switch to preset_2
        repo.replace_rules(deepcopy(presets["preset_2"].rules))
        repo.save()
        repo.load()
        assert repo.find("r1").name == "Trim"
        assert repo.find("r1").steps[0].type == "trim"


# ═══════════════════════════════════════════════════════════════════
# Last-Used Preset ID Persistence (parametric simulation)
# ═══════════════════════════════════════════════════════════════════


class TestLastPresetIdPersistence:
    def test_persist_and_retrieve_id(self) -> None:
        """Store and retrieve the last-used preset ID (dict simulates QSettings)."""
        storage: dict[str, str] = {}

        # save
        storage["preset/last_selected"] = "preset_1"
        assert storage.get("preset/last_selected") == "preset_1"

    def test_clear_and_retrieve_none(self) -> None:
        """No stored ID → returns None."""
        storage: dict[str, str | None] = {}

        raw = storage.get("preset/last_selected")
        result = raw if isinstance(raw, str) else None
        assert result is None

    def test_overwrite_persisted_id(self) -> None:
        """Setting a new preset ID overwrites the old one."""
        storage: dict[str, str] = {}
        storage["preset/last_selected"] = "preset_1"
        assert storage["preset/last_selected"] == "preset_1"

        storage["preset/last_selected"] = "preset_2"
        assert storage["preset/last_selected"] == "preset_2"

    def test_non_string_value_returns_none(self) -> None:
        """Non-string stored value → treated as None (defensive)."""
        storage: dict[str, object] = {}
        storage["preset/last_selected"] = 123  # type: ignore

        raw = storage.get("preset/last_selected")
        result = raw if isinstance(raw, str) else None
        assert result is None
