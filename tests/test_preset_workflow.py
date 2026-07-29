"""WP-23: Preset workflow integration tests — Repository ↔ PresetStore round-trip."""
from __future__ import annotations

import tempfile
from copy import deepcopy
from pathlib import Path

from editor.edit_session import EditSession
from models.preset import Preset
from models.rule import Rule
from models.rule_step import RuleStep
from storage.preset_store import PresetStore
from storage.repository import RuleRepository


def _repo_with_rules() -> RuleRepository:
    td = tempfile.mkdtemp()
    repo = RuleRepository(Path(td) / "rules.json")
    repo.load()
    repo.add(Rule(id="r1", name="Rule A", steps=[
        RuleStep(type="replace", parameters={"from": "a", "to": "b"}),
    ]))
    repo.add(Rule(id="r2", name="Rule B"))
    repo.save()
    return repo


def _preset_store() -> PresetStore:
    td = tempfile.mkdtemp()
    return PresetStore(Path(td) / "presets.json")


# ═══════════════════════════════════════════════════════════════════
# Preset Save / Load Workflow
# ═══════════════════════════════════════════════════════════════════


class TestPresetSaveLoad:
    def test_save_and_load_preserves_all_rules(self) -> None:
        repo = _repo_with_rules()
        store = _preset_store()

        # save
        preset = Preset(
            id=store._next_id(),
            name="My Preset",
            rules=deepcopy(repo.all_rules()),
        )
        store.save(preset)

        # verify on disk
        store2 = PresetStore(store._path)
        loaded = store2.load_all()
        assert len(loaded) == 1
        assert len(loaded[0].rules) == 2

        # load into a fresh repo
        new_repo = RuleRepository(Path(tempfile.mkdtemp()) / "rules.json")
        new_repo.load()
        new_repo.replace_rules(deepcopy(loaded[0].rules))
        new_repo.save()

        new_repo.load()
        assert len(new_repo.all_rules()) == 2
        assert new_repo.find("r1").steps[0].parameters["from"] == "a"
        assert new_repo.find("r1").steps[0].parameters["to"] == "b"

    def test_load_overwrites_existing_rules(self) -> None:
        repo = _repo_with_rules()
        store = _preset_store()

        # save with one rule
        preset = Preset(
            id=store._next_id(),
            name="Single Rule",
            rules=deepcopy([repo.all_rules()[0]]),
        )
        store.save(preset)

        # load → replaces existing 2 rules with 1
        repo.replace_rules(deepcopy(store.load_all()[0].rules))
        repo.save()
        repo.load()
        assert len(repo.all_rules()) == 1
        assert repo.find("r1") is not None
        assert repo.find("r2") is None

    def test_save_empty_repo(self) -> None:
        td = tempfile.mkdtemp()
        repo = RuleRepository(Path(td) / "rules.json")
        repo.load()
        store = _preset_store()

        preset = Preset(
            id=store._next_id(),
            name="Empty",
            rules=[],
        )
        store.save(preset)

        loaded = PresetStore(store._path).load_all()
        assert loaded[0].rules == []

    def test_save_overwrite_existing_preset_by_name(self) -> None:
        """Save with same name overwrites existing preset."""
        repo = _repo_with_rules()
        store = _preset_store()

        # first save
        p1 = Preset(id=store._next_id(), name="Same Name", rules=deepcopy(repo.all_rules()))
        store.save(p1)

        # second save — same name, different rules
        p2 = Preset(id=p1.id, name="Same Name", rules=[])
        store.save(p2)

        loaded = store.load_all()
        assert len(loaded) == 1
        assert loaded[0].rules == []


# ═══════════════════════════════════════════════════════════════════
# Preset — Dirty Session Interaction
# ═══════════════════════════════════════════════════════════════════


class TestPresetDirtySessionGuard:
    def test_dirty_session_detectable_before_load(self) -> None:
        repo = _repo_with_rules()
        rule = repo.find("r1")

        session = EditSession()
        session.open(rule)
        session.update_param(rule.steps[0].id, "to", "dirty_value")
        assert session.is_dirty() is True

    def test_load_preset_while_session_dirty_does_not_crash(self) -> None:
        """Loading a preset while session is dirty should be safe."""
        repo = _repo_with_rules()
        store = _preset_store()

        # save preset with current state
        preset = Preset(
            id=store._next_id(),
            name="Test",
            rules=deepcopy(repo.all_rules()),
        )
        store.save(preset)

        # make session dirty
        session = EditSession()
        session.open(repo.find("r1"))
        session.update_param(repo.find("r1").steps[0].id, "to", "dirty")

        # load preset — replaces repo rules
        repo.replace_rules(deepcopy(store.load_all()[0].rules))
        repo.save()

        # discard session to clean up
        session.discard()

        # verify repo loaded correctly
        repo.load()
        assert repo.find("r1").steps[0].parameters["to"] == "b"

    def test_session_discard_after_preset_load(self) -> None:
        """After load + discard, session should be clean."""
        repo = _repo_with_rules()
        store = _preset_store()

        preset = Preset(
            id=store._next_id(),
            name="Test",
            rules=deepcopy(repo.all_rules()),
        )
        store.save(preset)

        session = EditSession()
        session.open(repo.find("r1"))
        session.update_param(repo.find("r1").steps[0].id, "from", "x")

        # load preset + discard
        repo.replace_rules(deepcopy(store.load_all()[0].rules))
        session.discard()

        assert session.is_dirty() is False
        assert repo.find("r1").steps[0].parameters["from"] == "a"


# ═══════════════════════════════════════════════════════════════════
# Rule Independence After Preset Load
# ═══════════════════════════════════════════════════════════════════


class TestPresetRuleIndependence:
    def test_loaded_rules_are_independent_copies(self) -> None:
        """Mutating loaded rules must not affect the preset on disk."""
        repo = _repo_with_rules()
        store = _preset_store()

        preset = Preset(
            id=store._next_id(),
            name="Original",
            rules=deepcopy(repo.all_rules()),
        )
        store.save(preset)

        # load into repo
        repo.replace_rules(deepcopy(store.load_all()[0].rules))

        # mutate repo
        repo.find("r1").name = "MUTATED"
        repo.save()

        # reload preset from disk — should be unchanged
        loaded = PresetStore(store._path).load_all()
        assert loaded[0].rules[0].name == "Rule A"

    def test_load_then_save_as_new_preset_preserves_all(self) -> None:
        repo = _repo_with_rules()
        store = _preset_store()

        # load preset
        repo.replace_rules(deepcopy(repo.all_rules()))
        repo.save()

        # save as new preset
        preset = Preset(
            id=store._next_id(),
            name="Snapshot",
            rules=deepcopy(repo.all_rules()),
        )
        store.save(preset)

        loaded = PresetStore(store._path).load_all()
        assert len(loaded) == 1
        assert len(loaded[0].rules) == 2
