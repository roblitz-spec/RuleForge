"""WP-5: EditSession WorkingCopy — creation, isolation, dirty tracking, discard."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from editor.edit_session import EditSession, SessionState
from models.rule import Rule
from models.rule_step import RuleStep


# ═══════════════════════════════════════════════════════════════════
# Creation & Lifecycle
# ═══════════════════════════════════════════════════════════════════

class TestEditSessionCreation:
    def test_session_starts_in_created_state(self) -> None:
        assert EditSession().state == SessionState.CREATED

    def test_rule_not_accessible_before_open(self) -> None:
        with pytest.raises(RuntimeError, match="not ACTIVE"):
            _ = EditSession().rule

    def test_original_not_accessible_before_open(self) -> None:
        with pytest.raises(RuntimeError, match="session never opened"):
            _ = EditSession().original


class TestEditSessionLifecycle:
    def test_open_transitions_to_active(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        assert session.state == SessionState.ACTIVE

    def test_open_with_steps(self) -> None:
        session = EditSession()
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        rule = Rule(id="r1", name="Test", steps=[step])
        session.open(rule)
        assert session.state == SessionState.ACTIVE
        assert session.rule.name == "Test"
        assert len(session.rule.steps) == 1

    def test_cannot_open_twice(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        with pytest.raises(RuntimeError, match="Cannot open"):
            session.open(Rule(id="r2", name="Other"))

    def test_cannot_open_after_close(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        session.close()
        with pytest.raises(RuntimeError, match="Cannot open"):
            session.open(Rule(id="r2", name="Other"))

    def test_close_transitions_to_closed(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        session.close()
        assert session.state == SessionState.CLOSED

    def test_close_idempotent(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        session.close()
        session.close()
        assert session.state == SessionState.CLOSED

    def test_rule_not_accessible_after_close(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        session.close()
        with pytest.raises(RuntimeError, match="not ACTIVE"):
            _ = session.rule


# ═══════════════════════════════════════════════════════════════════
# WorkingCopy Isolation
# ═══════════════════════════════════════════════════════════════════

class TestWorkingCopyIsolation:
    """Editing the WorkingCopy must never affect the original Rule."""

    def test_rule_is_deep_copy_not_same_object(self) -> None:
        original = Rule(id="r1", name="Test",
                        steps=[RuleStep(type="replace", parameters={"from": "a", "to": "b"})])
        session = EditSession()
        session.open(original)
        assert session.rule is not original

    def test_step_objects_are_deep_copied(self) -> None:
        original = Rule(id="r1", name="Test",
                        steps=[RuleStep(type="replace", parameters={"from": "a", "to": "b"})])
        session = EditSession()
        session.open(original)
        assert session.rule.steps[0] is not original.steps[0]

    def test_original_preserved_after_mutation(self) -> None:
        original = Rule(id="r1", name="Test",
                        steps=[RuleStep(type="replace", parameters={"from": "a", "to": "b"})])
        orig_from = original.steps[0].parameters["from"]

        session = EditSession()
        session.open(original)
        session.update_param(original.steps[0].id, "from", "CHANGED")

        assert original.steps[0].parameters["from"] == orig_from  # unchanged
        assert session.rule.steps[0].parameters["from"] == "CHANGED"

    def test_original_accessible_via_property(self) -> None:
        original = Rule(id="r1", name="Test")
        session = EditSession()
        session.open(original)
        assert session.original is original

    def test_original_name_unchanged_after_working_copy_name_change(self) -> None:
        original = Rule(id="r1", name="Old Name")
        session = EditSession()
        session.open(original)
        session.rule.name = "New Name"
        assert session.original.name == "Old Name"
        assert session.rule.name == "New Name"


# ═══════════════════════════════════════════════════════════════════
# Dirty Tracking
# ═══════════════════════════════════════════════════════════════════

class TestDirtyTracking:
    def test_not_dirty_after_open(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test",
                          steps=[RuleStep(type="replace", parameters={"from": "a"})]))
        assert session.is_dirty() is False

    def test_dirty_after_update_param(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "changed")
        assert session.is_dirty() is True

    def test_dirty_after_multiple_updates(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "x")
        session.update_param(step.id, "to", "y")
        assert session.is_dirty() is True

    def test_not_dirty_if_value_unchanged(self) -> None:
        """update_param sets dirty even if value is the same (simplest tracking)."""
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "a")  # same value
        assert session.is_dirty() is True  # still marks dirty


# ═══════════════════════════════════════════════════════════════════
# update_param
# ═══════════════════════════════════════════════════════════════════

class TestUpdateParam:
    def test_update_existing_step(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.rule.steps[0].parameters["from"] == "X"

    def test_update_param_requires_active(self) -> None:
        session = EditSession()
        with pytest.raises(RuntimeError, match="not ACTIVE"):
            session.update_param("any", "key", "val")

    def test_update_param_unknown_step_raises(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        with pytest.raises(ValueError, match="not found"):
            session.update_param("nonexistent", "key", "val")

    def test_update_param_preserves_other_params(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.rule.steps[0].parameters["to"] == "b"


# ═══════════════════════════════════════════════════════════════════
# Discard (local revert)
# ═══════════════════════════════════════════════════════════════════

class TestDiscard:
    def test_discard_reverts_to_original(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "CHANGED")
        session.discard()
        assert session.rule.steps[0].parameters["from"] == "a"

    def test_discard_clears_dirty(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "CHANGED")
        assert session.is_dirty() is True
        session.discard()
        assert session.is_dirty() is False

    def test_discard_noop_when_no_original(self) -> None:
        session = EditSession()
        session.discard()  # no-op, no crash

    def test_working_copy_is_deep_copy_after_discard(self) -> None:
        """After discard, WorkingCopy is a new deep copy — not the original reference."""
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "CHANGED")
        session.discard()
        assert session.rule is not session.original


# ═══════════════════════════════════════════════════════════════════
# Stubs (not yet implemented)
# ═══════════════════════════════════════════════════════════════════

class TestStubs:
    def test_commit_raises_not_implemented(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        with pytest.raises(NotImplementedError, match="WP-8"):
            session.commit()


# ═══════════════════════════════════════════════════════════════════
# WP-6: UI Integration Scenario
# ═══════════════════════════════════════════════════════════════════

class TestUIIntegrationScenario:
    """Simulates the RuleManagerDialog EditSession integration flow."""

    def test_ui_flow_select_edit_save(self) -> None:
        """Simulate: select rule → edit via session → save persists changes."""
        from storage.repository import RuleRepository

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8",
        ) as f:
            json.dump({
                "version": 1,
                "rules": [{
                    "id": "r1", "name": "Old Name", "description": "",
                    "pinned": False,
                    "steps": [
                        {"type": "replace", "parameters": {"from": "a", "to": "b"}},
                    ],
                }],
            }, f, ensure_ascii=False)
            tmp = Path(f.name)

        try:
            repo = RuleRepository(tmp)
            repo.load()

            # Simulate _on_rule_selected: find rule → create session → swap to WorkingCopy
            repo_rule = repo.find("r1")
            assert repo_rule is not None
            session = EditSession()
            session.open(repo_rule)
            rule = session.rule  # WorkingCopy
            repo.update(rule)

            # Simulate _on_param_changed: edit through session
            step = rule.steps[0]
            session.update_param(step.id, "from", "X")
            session.update_param(step.id, "to", "Y")

            # WorkingCopy is dirty, original is preserved
            assert session.is_dirty() is True
            assert session.original.steps[0].parameters["from"] == "a"

            # Simulate _on_save: save repo (which now has WorkingCopy)
            rule.name = "New Name"
            repo.save()

            # Verify persistence
            repo2 = RuleRepository(tmp)
            repo2.load()
            loaded = repo2.find("r1")
            assert loaded is not None
            assert loaded.name == "New Name"
            assert loaded.steps[0].parameters["from"] == "X"
            assert loaded.steps[0].parameters["to"] == "Y"
        finally:
            tmp.unlink()

    def test_discard_reverts_ui_changes(self) -> None:
        """Simulate: edit → discard → WorkingCopy matches original."""
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        original = Rule(id="r1", name="Test", steps=[step])

        session = EditSession()
        session.open(original)

        session.update_param(original.steps[0].id, "from", "CHANGED")
        assert session.is_dirty() is True
        assert session.rule.steps[0].parameters["from"] == "CHANGED"

        session.discard()
        assert session.is_dirty() is False
        assert session.rule.steps[0].parameters["from"] == "a"
        # After discard, WorkingCopy values equal original
        assert session.rule.steps[0].parameters == session.original.steps[0].parameters

    def test_no_direct_rule_mutation(self) -> None:
        """UI integration: all edits go through session.update_param."""
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        original = Rule(id="r1", name="Test", steps=[step])

        session = EditSession()
        session.open(original)

        # This is what _on_param_changed does after WP-6
        sid = session.rule.steps[0].id
        session.update_param(sid, "from", "UI_VALUE")

        # WorkingCopy has the change
        assert session.rule.steps[0].parameters["from"] == "UI_VALUE"
        # Original is untouched
        assert session.original.steps[0].parameters["from"] == "a"


# ═══════════════════════════════════════════════════════════════════
# SessionState
# ═══════════════════════════════════════════════════════════════════

class TestSessionStateEnum:
    def test_states_are_distinct(self) -> None:
        assert SessionState.CREATED is not SessionState.ACTIVE
        assert SessionState.ACTIVE is not SessionState.CLOSED
        assert SessionState.CREATED is not SessionState.CLOSED

    def test_all_states_exist(self) -> None:
        states = set(SessionState)
        assert len(states) == 3
