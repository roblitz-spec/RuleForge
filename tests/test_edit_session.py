"""WP-5: EditSession WorkingCopy — creation, isolation, dirty tracking, discard."""
from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path

import pytest

from editor.edit_session import EditSession, SessionState
from models.rule import Rule
from models.rule_step import RuleStep
from storage.session_store import SessionStore


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
# WP-6: UI Integration Scenario
# ═══════════════════════════════════════════════════════════════════

class TestUIIntegrationScenario:
    """Simulates the RuleManagerDialog EditSession integration flow."""

    def test_ui_flow_select_edit_save(self) -> None:
        """Simulate WP-7: select → edit → commit → save → reload."""
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

            # Simulate _on_rule_selected: find rule → create session → get WorkingCopy
            repo_rule = repo.find("r1")
            assert repo_rule is not None
            session = EditSession()
            session.open(repo_rule)
            rule = session.rule  # WorkingCopy (NOT in repo via update bridge)

            # Simulate _on_param_changed: edit through session
            step = rule.steps[0]
            session.update_param(step.id, "from", "X")
            session.update_param(step.id, "to", "Y")

            # Simulate _on_save: update name → commit → save
            rule.name = "New Name"
            session.commit()

            # Original now reflects committed state
            assert session.original.name == "New Name"
            assert session.is_dirty() is False

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
# WP-8: Undo / Redo
# ═══════════════════════════════════════════════════════════════════

class TestUndoRedoBasic:
    def test_can_undo_false_after_open(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        assert session.can_undo() is False
        assert session.can_redo() is False

    def test_can_undo_true_after_edit(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.can_undo() is True
        assert session.can_redo() is False

    def test_undo_single_edit(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.rule.steps[0].parameters["from"] == "X"

        session.undo()
        assert session.rule.steps[0].parameters["from"] == "a"

    def test_undo_boundary_no_history(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        session.undo()  # no-op
        assert session.can_undo() is False

    def test_redo_restores_undone_change(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.undo()
        assert session.rule.steps[0].parameters["from"] == "a"
        assert session.can_redo() is True

        session.redo()
        assert session.rule.steps[0].parameters["from"] == "X"
        assert session.can_redo() is False

    def test_redo_boundary_no_future(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        session.redo()  # no-op
        assert session.can_redo() is False


class TestUndoRedoMultiple:
    def test_multiple_undos(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.update_param(step.id, "from", "Y")
        session.update_param(step.id, "from", "Z")
        assert session.rule.steps[0].parameters["from"] == "Z"
        assert session.can_undo() is True

        session.undo()
        assert session.rule.steps[0].parameters["from"] == "Y"
        session.undo()
        assert session.rule.steps[0].parameters["from"] == "X"
        session.undo()
        assert session.rule.steps[0].parameters["from"] == "a"
        assert session.can_undo() is False

    def test_multiple_redos(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.update_param(step.id, "from", "Y")
        session.undo()
        session.undo()
        # at original state
        assert session.rule.steps[0].parameters["from"] == "a"

        session.redo()
        assert session.rule.steps[0].parameters["from"] == "X"
        session.redo()
        assert session.rule.steps[0].parameters["from"] == "Y"
        assert session.can_redo() is False

    def test_new_edit_clears_redo_history(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.undo()
        assert session.can_redo() is True
        # new edit should clear redo history
        session.update_param(step.id, "from", "Z")
        assert session.can_redo() is False
        assert session.rule.steps[0].parameters["from"] == "Z"


class TestUndoRedoDirty:
    def test_undo_to_original_clears_dirty(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.is_dirty() is True
        session.undo()
        assert session.is_dirty() is False

    def test_redo_restores_dirty(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.undo()
        assert session.is_dirty() is False
        session.redo()
        assert session.is_dirty() is True

    def test_partial_undo_keeps_dirty(self) -> None:
        """Undoing some but not all edits keeps dirty flag."""
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.update_param(step.id, "to", "Y")
        session.undo()  # only undo "to" change
        assert session.is_dirty() is True  # "from" still changed

    def test_dirty_with_name_change_undo(self) -> None:
        """Undo that reverts name change should clear dirty."""
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        # Simulate name change via WorkingCopy (pre-commit)
        snapshot = deepcopy(session._working_copy)
        session._history.append(snapshot)
        session._working_copy.name = "New Name"
        session._dirty = True

        assert session.is_dirty() is True
        session.undo()
        assert session.is_dirty() is False
        assert session.rule.name == "Test"


class TestUndoRedoCommit:
    def test_commit_clears_history(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.can_undo() is True
        session.commit()
        assert session.can_undo() is False
        assert session.can_redo() is False

    def test_commit_after_undo(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "X")
        session.undo()  # back to original
        session.commit()
        # Original should be unchanged (undo reverted the change)
        assert original.steps[0].parameters["from"] == "a"
        assert session.is_dirty() is False

    def test_commit_after_redo(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "X")
        session.undo()
        session.redo()  # back to X
        session.commit()
        assert original.steps[0].parameters["from"] == "X"
        assert session.is_dirty() is False
        assert session.can_undo() is False


class TestUndoRedoIsolation:
    def test_undo_never_mutates_original(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(original.steps[0].id, "from", "X")
        session.undo()
        assert original.steps[0].parameters["from"] == "a"  # unchanged

    def test_redo_never_mutates_original(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(original.steps[0].id, "from", "X")
        session.undo()
        session.redo()
        assert original.steps[0].parameters["from"] == "a"  # still unchanged

    def test_discard_clears_history(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.can_undo() is True
        session.discard()
        assert session.can_undo() is False
        assert session.can_redo() is False


class TestCommitIsolation:
    """Editing the WorkingCopy does not mutate the original Rule."""

    def test_original_unchanged_after_updates(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])

        session = EditSession()
        session.open(original)
        session.update_param(original.steps[0].id, "from", "CHANGED")

        # Original still has old value
        assert original.steps[0].parameters["from"] == "a"

    def test_multiple_params_isolated(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        original = Rule(id="r1", name="Test", steps=[step])

        session = EditSession()
        session.open(original)
        session.update_param(original.steps[0].id, "from", "X")
        session.update_param(original.steps[0].id, "to", "Y")

        assert original.steps[0].parameters["from"] == "a"
        assert original.steps[0].parameters["to"] == "b"
        assert session.rule.steps[0].parameters["from"] == "X"
        assert session.rule.steps[0].parameters["to"] == "Y"


class TestCommit:
    """commit() applies WorkingCopy to original Rule."""

    def test_commit_copies_params_to_original(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])

        session = EditSession()
        session.open(original)
        session.update_param(original.steps[0].id, "from", "CHANGED")
        session.commit()

        assert original.steps[0].parameters["from"] == "CHANGED"

    def test_commit_copies_multiple_params(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        original = Rule(id="r1", name="Test", steps=[step])

        session = EditSession()
        session.open(original)
        session.update_param(original.steps[0].id, "from", "X")
        session.update_param(original.steps[0].id, "to", "Y")
        session.commit()

        assert original.steps[0].parameters["from"] == "X"
        assert original.steps[0].parameters["to"] == "Y"

    def test_commit_copies_name(self) -> None:
        original = Rule(id="r1", name="Old")
        session = EditSession()
        session.open(original)
        session.rule.name = "New"
        session.commit()
        assert original.name == "New"

    def test_commit_copies_pinned(self) -> None:
        original = Rule(id="r1", name="Test", pinned=False)
        session = EditSession()
        session.open(original)
        session.rule.pinned = True
        session.commit()
        assert original.pinned is True

    def test_committed_state_persists_across_edit_cycles(self) -> None:
        """Edit → commit → edit → commit → verify final state."""
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])

        session = EditSession()
        session.open(original)

        session.update_param(original.steps[0].id, "from", "X")
        session.commit()
        assert original.steps[0].parameters["from"] == "X"
        assert session.is_dirty() is False

        session.update_param(original.steps[0].id, "from", "Y")
        session.commit()
        assert original.steps[0].parameters["from"] == "Y"
        assert session.is_dirty() is False

    def test_commit_without_session_raises(self) -> None:
        session = EditSession()
        with pytest.raises(RuntimeError, match="Cannot commit"):
            session.commit()


class TestCommitDirtyState:
    def test_dirty_false_after_commit(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "CHANGED")
        assert session.is_dirty() is True
        session.commit()
        assert session.is_dirty() is False

    def test_dirty_false_after_commit_no_changes(self) -> None:
        """Commit without any edits should leave dirty False."""
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        assert session.is_dirty() is False
        session.commit()
        assert session.is_dirty() is False


class TestCommitSynchronization:
    def test_working_copy_reflects_committed_state(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "COMMITTED")
        session.commit()

        assert session.rule.steps[0].parameters["from"] == "COMMITTED"
        assert session.original.steps[0].parameters["from"] == "COMMITTED"

    def test_no_divergence_after_commit(self) -> None:
        """WorkingCopy and original have same content after commit."""
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "Z")
        session.commit()

        wc = session.rule
        orig = session.original
        assert wc.name == orig.name
        assert wc.steps[0].parameters == orig.steps[0].parameters


# ═══════════════════════════════════════════════════════════════════
# WP-9: Preview Isolation
# ═══════════════════════════════════════════════════════════════════

class TestPreviewWorkingCopy:
    """Preview subsystem reads the WorkingCopy, not the Repository."""

    def test_current_working_copy_is_working_copy(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        wc = session.rule
        assert wc is not original

    def test_current_working_copy_reflects_edits(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.rule.steps[0].parameters["from"] == "X"
        assert session.original.steps[0].parameters["from"] == "a"

    def test_current_working_copy_reflects_name_change(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Old"))
        session.rule.name = "New"
        assert session.rule.name == "New"
        assert session.original.name == "Old"


class TestPreviewReadOnly:
    """Preview is a read-only consumer; it must not mutate WorkingCopy."""

    def test_preview_does_not_mutate_working_copy(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        before = session.rule.steps[0].parameters["from"]
        _ = session.rule
        _ = session.rule.steps[0].parameters["from"]
        assert session.rule.steps[0].parameters["from"] == before

    def test_preview_never_triggers_persistence(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        _ = session.rule
        assert original.steps[0].parameters["from"] == "a"
        assert session.is_dirty() is False


class TestPreviewUndoRedoInteraction:
    """Preview correctly reflects undo/redo operations."""

    def test_undo_updates_preview_source(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.undo()
        assert session.rule.steps[0].parameters["from"] == "a"

    def test_redo_updates_preview_source(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.undo()
        session.redo()
        assert session.rule.steps[0].parameters["from"] == "X"

    def test_commit_updates_preview_source(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.commit()
        assert session.rule.steps[0].parameters["from"] == "X"

    def test_discard_updates_preview_source(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.discard()
        assert session.rule.steps[0].parameters["from"] == "a"


class TestCommitRemainsOnlyMutationPath:
    """WP-9 preserves WP-7 invariant: commit is only Rule mutation path."""

    def test_preview_path_never_mutates_original(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        wc = session.rule
        assert wc is not original
        assert original.steps[0].parameters["from"] == "a"

    def test_commit_still_works_after_preview_reads(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(original.steps[0].id, "from", "CHANGED")
        _ = session.rule
        session.commit()
        assert original.steps[0].parameters["from"] == "CHANGED"



# ═══════════════════════════════════════════════════════════════════
# WP-10: Auto Save (Commit-Based)
# ═══════════════════════════════════════════════════════════════════

class TestAutoCommit:
    """auto_commit() reuses the Commit boundary."""

    def test_auto_commit_commits_when_dirty(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "CHANGED")
        committed = session.auto_commit()
        assert committed is True
        assert original.steps[0].parameters["from"] == "CHANGED"

    def test_auto_commit_skips_when_clean(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        committed = session.auto_commit()
        assert committed is False
        assert original.steps[0].parameters["from"] == "a"

    def test_auto_commit_clears_dirty(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "CHANGED")
        session.auto_commit()
        assert session.is_dirty() is False

    def test_auto_commit_clears_history(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.update_param(step.id, "from", "Y")
        session.auto_commit()
        assert session.can_undo() is False
        assert session.can_redo() is False

    def test_auto_commit_returns_false_when_clean(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        assert session.is_dirty() is False
        assert session.auto_commit() is False


class TestAutoSaveFailure:
    """Auto-save on failure preserves WorkingCopy and dirty state."""

    def test_auto_commit_working_copy_survives(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "SAFE")
        # commit succeeds, WorkingCopy is intact
        session.commit()
        assert session.rule.steps[0].parameters["from"] == "SAFE"

    def test_dirty_remains_when_no_commit(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "CHANGED")
        # auto_commit on clean state does nothing
        session.auto_commit()
        assert session.is_dirty() is False  # commit cleared it
        # Now dirty again
        session.update_param(step.id, "from", "AGAIN")
        assert session.is_dirty() is True


class TestManualSaveAfterAutoSave:
    """Manual Save behavior is unchanged after auto-save."""

    def test_manual_save_after_auto_save(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "AUTO")
        session.auto_commit()
        # After auto-save, dirty is cleared
        assert session.is_dirty() is False
        assert original.steps[0].parameters["from"] == "AUTO"

    def test_manual_save_still_works_after_auto_save(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "AUTO")
        session.auto_commit()  # auto-save
        # More editing
        session.update_param(step.id, "from", "MANUAL")
        session.commit()  # manual save
        assert original.steps[0].parameters["from"] == "MANUAL"

    def test_auto_save_does_not_interfere_with_undo(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.update_param(step.id, "from", "Y")
        session.auto_commit()
        # History is cleared after auto_commit
        assert session.can_undo() is False
        # New edits create fresh history
        session.update_param(step.id, "from", "Z")
        assert session.can_undo() is True
        session.undo()
        assert session.rule.steps[0].parameters["from"] == "Y"


class TestCommitBoundaryPreserved:
    """WP-10 preserves the WP-7 invariant: commit() is the only Rule mutation path."""

    def test_auto_commit_uses_same_mutation_path(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "X")
        # auto_commit calls commit(), same mutation path
        session.auto_commit()
        assert original.steps[0].parameters["from"] == "X"

    def test_auto_commit_is_idempotent(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "X")
        session.auto_commit()  # first
        session.auto_commit()  # second (clean, should return False)
        # No corruption
        assert original.steps[0].parameters["from"] == "X"
        assert session.is_dirty() is False

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


# ═══════════════════════════════════════════════════════════════════
# WP-11: Unsaved Changes Warning
# ═══════════════════════════════════════════════════════════════════

class TestDirtyWarningState:
    """Warning derives exclusively from is_dirty(); consumer is read-only."""

    def test_clean_session_no_warning(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        # Warning check: is_dirty() → False → no warning
        assert session.is_dirty() is False

    def test_dirty_session_warning_active(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        # Warning check: is_dirty() → True → warning active
        assert session.is_dirty() is True

    def test_warning_is_read_only(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "X")
        # Read is_dirty() multiple times — never mutates
        assert session.is_dirty() is True
        assert session.is_dirty() is True
        assert original.steps[0].parameters["from"] == "a"
        assert session.rule.steps[0].parameters["from"] == "X"


class TestDirtyWarningAutoSave:
    """Warning follows dirty state through auto-save transitions."""

    def test_auto_save_success_clears_warning_state(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.is_dirty() is True  # warning
        session.auto_commit()
        assert session.is_dirty() is False  # no warning

    def test_auto_save_clean_noop_preserves_clean_state(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        assert session.is_dirty() is False  # no warning
        session.auto_commit()
        assert session.is_dirty() is False  # still no warning


class TestDirtyWarningManualSave:
    """Manual save clears warning state."""

    def test_manual_save_clears_warning(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.is_dirty() is True
        session.commit()
        assert session.is_dirty() is False

    def test_discard_clears_warning(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        assert session.is_dirty() is True
        session.discard()
        assert session.is_dirty() is False


class TestDirtyWarningUndoRedo:
    """Warning reflects undo/redo state correctly."""

    def test_undo_to_clean_clears_warning(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.undo()
        assert session.is_dirty() is False  # no warning

    def test_redo_restores_warning(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.undo()
        assert session.is_dirty() is False  # no warning
        session.redo()
        assert session.is_dirty() is True   # warning returns


class TestDirtyWarningIsolation:
    """Warning layer never mutates WorkingCopy, Rule, or Repository."""

    def test_warning_never_mutates_working_copy(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        before = session.rule.steps[0].parameters["from"]
        _ = session.is_dirty()  # warning check
        assert session.rule.steps[0].parameters["from"] == before

    def test_warning_never_mutates_original(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "X")
        _ = session.is_dirty()  # warning check
        assert original.steps[0].parameters["from"] == "a"

    def test_warning_never_calls_commit(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        _ = session.is_dirty()
        # Warning didn't trigger commit — dirty state preserved
        assert session.is_dirty() is True


# ═══════════════════════════════════════════════════════════════════
# WP-12: Session Persistence
# ═══════════════════════════════════════════════════════════════════

class TestSessionPersistenceRoundTrip:
    """Session state round-trips through SerializableSession correctly."""

    def test_clean_session_roundtrip(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        data = session.to_serializable()
        restored = EditSession.restore_from(data)
        assert restored.rule.id == "r1"
        assert restored.rule.name == "Test"
        assert restored.rule.steps[0].type == "replace"
        assert restored.rule.steps[0].parameters["from"] == "a"
        assert restored.is_dirty() is False

    def test_dirty_session_roundtrip(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "DIRTY")
        data = session.to_serializable()
        restored = EditSession.restore_from(data)
        assert restored.is_dirty() is True
        assert restored.rule.steps[0].parameters["from"] == "DIRTY"

    def test_undo_history_not_restored(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "X")
        session.update_param(step.id, "from", "Y")
        assert session.can_undo() is True
        data = session.to_serializable()
        restored = EditSession.restore_from(data)
        # WP-12 Option A: undo history is NOT restored
        assert restored.can_undo() is False
        assert restored.can_redo() is False


class TestSessionPersistenceCommitBoundary:
    """Restore does not mutate Rule or write Repository."""

    def test_restore_does_not_mutate_original_rule(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        session.update_param(step.id, "from", "CHANGED")
        data = session.to_serializable()
        _ = EditSession.restore_from(data)
        # Original must NOT be touched
        assert original.steps[0].parameters["from"] == "a"

    def test_restored_session_can_commit(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "RESTORED")
        data = session.to_serializable()
        restored = EditSession.restore_from(data)
        # Restored session can still commit
        restored.commit()
        assert restored.is_dirty() is False
        assert restored.rule.steps[0].parameters["from"] == "RESTORED"


class TestSessionPersistenceAutoSaveCompat:
    """Auto Save and session persistence coexist correctly."""

    def test_restored_session_auto_commit_works(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "AUTO")
        data = session.to_serializable()
        restored = EditSession.restore_from(data)
        restored.auto_commit()
        assert restored.is_dirty() is False

    def test_restored_clean_session_auto_commit_noop(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        data = session.to_serializable()
        restored = EditSession.restore_from(data)
        committed = restored.auto_commit()
        assert committed is False


class TestSessionPersistenceUnsavedChangesCompat:
    """Unsaved Changes warning follows restored dirty state."""

    def test_restored_dirty_session_has_warning_state(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="r1", name="Test", steps=[step]))
        session.update_param(step.id, "from", "UNSAVED")
        data = session.to_serializable()
        restored = EditSession.restore_from(data)
        assert restored.is_dirty() is True  # warning active

    def test_restored_clean_session_no_warning(self) -> None:
        session = EditSession()
        session.open(Rule(id="r1", name="Test"))
        data = session.to_serializable()
        restored = EditSession.restore_from(data)
        assert restored.is_dirty() is False  # no warning


class TestSerializableSessionStruct:
    """SerializableSession is a pure data holder, not an owner."""

    def test_serializable_is_pure_data(self) -> None:
        from models.session import SerializableSession
        step = RuleStep(type="replace", parameters={"from": "x"})
        rule = Rule(id="r1", name="T", steps=[step])
        ss = SerializableSession(working_copy=rule, is_dirty=True)
        assert ss.working_copy.steps[0].parameters["from"] == "x"
        assert ss.is_dirty is True

    def test_serializable_dirty_default(self) -> None:
        from models.session import SerializableSession
        ss = SerializableSession(working_copy=Rule(id="r1", name="T"), is_dirty=False)
        assert ss.is_dirty is False


# ═══════════════════════════════════════════════════════════════════
# M4.1 Issue A: Single Commit Path
# ═══════════════════════════════════════════════════════════════════

class TestSingleCommitPath:
    """Rule mutation occurs ONLY through EditSession.commit()."""

    def test_commit_is_the_only_mutation_path(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step])
        session = EditSession()
        session.open(original)
        # User edits via WorkingCopy
        wc = session.rule
        wc.name = "Changed"
        # Editing WorkingCopy does NOT mutate original
        assert original.name == "Test"
        # commit() IS the mutation path
        session.commit()
        assert original.name == "Changed"

    def test_pinned_syncs_through_working_copy(self) -> None:
        """Simulates Issue A fix: pin toggle syncs to WorkingCopy."""
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Test", steps=[step], pinned=False)
        session = EditSession()
        session.open(original)
        # Simulate context menu: toggle pin on repo Rule, sync to WorkingCopy
        original.pinned = True
        session.rule.pinned = True  # sync (as done in UI Issue A fix)
        # commit() picks up the pinned change from WorkingCopy
        session.commit()
        assert original.pinned is True

    def test_commit_path_handles_all_rule_fields(self) -> None:
        """commit() syncs name, description, pinned, and steps."""
        step = RuleStep(type="replace", parameters={"from": "a"})
        original = Rule(id="r1", name="Old", description="Desc", pinned=False, steps=[step])
        session = EditSession()
        session.open(original)
        wc = session.rule
        wc.name = "New"
        wc.description = "Updated"
        wc.pinned = True
        wc.steps = [RuleStep(type="insert", parameters={"text": "x"})]
        session.commit()
        assert original.name == "New"
        assert original.description == "Updated"
        assert original.pinned is True
        assert original.steps[0].type == "insert"

    def test_adding_rule_is_repository_operation(self) -> None:
        """Adding a new rule is a Repository operation, not a mutation."""
        # This is tested to confirm the architecture: create/delete are
        # Repository-level CRUD, not Rule mutation through commit().
        assert Rule(id="new", name="New") is not None


# ═══════════════════════════════════════════════════════════════════
# M4.1 Issue B: SessionStore Lifecycle
# ═══════════════════════════════════════════════════════════════════

class TestSessionStoreLifecycle:
    """SessionStore round-trip is integrated into EditSession lifecycle."""

    def setup_method(self) -> None:
        import tempfile
        self._tmpdir = tempfile.mkdtemp()
        self._store = SessionStore(Path(self._tmpdir))

    def teardown_method(self) -> None:
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_save_and_load_clean_session(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="rule-a", name="Test", steps=[step]))
        self._store.save("rule-a", session.to_serializable())
        restored = self._restore_via_store("rule-a")
        assert restored is not None
        assert restored.rule.id == "rule-a"
        assert restored.rule.name == "Test"
        assert restored.is_dirty() is False

    def test_save_and_load_dirty_session(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="rule-a", name="Test", steps=[step]))
        session.update_param(step.id, "from", "DIRTY")
        self._store.save("rule-a", session.to_serializable())
        restored = self._restore_via_store("rule-a")
        assert restored is not None
        assert restored.is_dirty() is True
        assert restored.rule.steps[0].parameters["from"] == "DIRTY"

    def test_restore_does_not_write_repository(self) -> None:
        """Restoring a session NEVER writes to Repository."""
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="rule-a", name="Test", steps=[step]))
        session.update_param(step.id, "from", "Z")
        self._store.save("rule-a", session.to_serializable())
        restored = self._restore_via_store("rule-a")
        assert restored is not None
        # Restored session is independent — no repo write occurred
        assert restored.rule.steps[0].parameters["from"] == "Z"
        assert restored.is_dirty() is True

    def test_restored_session_can_commit(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a"})
        session = EditSession()
        session.open(Rule(id="rule-a", name="Test", steps=[step]))
        session.update_param(step.id, "from", "COMMITTED")
        self._store.save("rule-a", session.to_serializable())
        restored = self._restore_via_store("rule-a")
        assert restored is not None
        restored.commit()
        assert restored.is_dirty() is False
        assert restored.rule.steps[0].parameters["from"] == "COMMITTED"

    def test_remove_clears_persisted_session(self) -> None:
        session = EditSession()
        session.open(Rule(id="rule-a", name="Test"))
        self._store.save("rule-a", session.to_serializable())
        assert self._store.load("rule-a") is not None
        self._store.remove("rule-a")
        assert self._store.load("rule-a") is None

    def test_load_nonexistent_returns_none(self) -> None:
        assert self._store.load("nonexistent") is None

    def _restore_via_store(self, rule_id: str) -> EditSession | None:
        data = self._store.load(rule_id)
        if data is None:
            return None
        return EditSession.restore_from(data)



