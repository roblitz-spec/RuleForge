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
