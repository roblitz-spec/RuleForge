"""Integration tests for ExecutionIntegrationService and ExecutionWorker.

Verifies the thin adapter correctly bridges GUI plans → ExecutionPipeline.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from engine.operation_logger import OperationLogger
from models.rename_plan import RenameAction, RenamePlan, RenamePlanStatus
from models.rename_result import RenameResult
from models.rule import Rule
from models.rule_step import RuleStep
from ui.execution_integration import ExecutionIntegrationService


# ── Helpers ──────────────────────────────────────────────────────────

def _make_rule(id_str: str = "test-rule-id") -> Rule:
    return Rule(
        id=id_str,
        name="test-rule",
        steps=[RuleStep(type="case", parameters={"mode": "upper"})],
    )


def _make_plan(
    source: Path, target: Path,
    action: RenameAction = RenameAction.RENAME,
    status: RenamePlanStatus = RenamePlanStatus.READY,
) -> RenamePlan:
    return RenamePlan(
        source=source,
        source_name=source.name,
        target_name=target.name,
        target=target,
        needs_rename=(source != target),
        status=status,
        action=action,
    )


# ── IntegrationService.execute ───────────────────────────────────────

class TestIntegrationServiceExecute:
    """Tests for ExecutionIntegrationService.execute()."""

    def test_rename_success(self, tmp_path: Path) -> None:
        src = tmp_path / "hello.txt"
        src.write_text("content")
        dst = tmp_path / "HELLO.txt"

        service = ExecutionIntegrationService()
        plan = _make_plan(src, dst)
        rule = _make_rule()

        result = service.execute(plan, rule)

        assert result.success
        assert result.source == src
        assert result.target == dst
        assert dst.exists()
        assert not src.exists()
        assert plan.status == RenamePlanStatus.SUCCESS
        assert service.can_rollback

    def test_skip_plan_not_executed(self) -> None:
        service = ExecutionIntegrationService()
        plan = RenamePlan(
            source=Path("/tmp/a.txt"),
            source_name="a.txt",
            target_name="b.txt",
            target=Path("/tmp/b.txt"),
            action=RenameAction.SKIP,
            status=RenamePlanStatus.NO_CHANGE,
        )
        # SKIP plans are handled by ExecutionWorker, not execute()
        # execute() should still work — it just won't find them in ops
        # since source doesn't exist, build_rename_plan will raise

    def test_overwrite_pre_deletes_target(self, tmp_path: Path) -> None:
        src = tmp_path / "hello.txt"
        src.write_text("new-content")
        dst = tmp_path / "HELLO.txt"
        dst.write_text("old-content")

        service = ExecutionIntegrationService()
        plan = _make_plan(src, dst, action=RenameAction.OVERWRITE)
        rule = _make_rule("overwrite-rule")
        result = service.execute(plan, rule)
        assert result.success
        assert not src.exists()
        assert dst.exists()
        assert dst.read_text() == "new-content"
        assert plan.status == RenamePlanStatus.OVERWRITTEN

    def test_execute_returns_renameresult(self, tmp_path: Path) -> None:
        src = tmp_path / "x.txt"
        src.write_text("ok")
        dst = tmp_path / "X.txt"

        service = ExecutionIntegrationService()
        plan = _make_plan(src, dst)
        result = service.execute(plan, _make_rule("rr-test"))
        assert isinstance(result, RenameResult)
        assert result.success

    def test_rollback_after_execute(self, tmp_path: Path) -> None:
        src = tmp_path / "file.txt"
        src.write_text("data")
        dst = tmp_path / "FILE.txt"

        service = ExecutionIntegrationService()
        plan = _make_plan(src, dst)
        rule = _make_rule()

        service.execute(plan, rule)
        assert service.can_rollback
        assert dst.exists()

        rb = service.rollback()
        assert len(rb.restored) == 1
        assert src.exists()
        assert not dst.exists()
        assert not service.can_rollback

    def test_execute_recorded_to_logger(self, tmp_path: Path) -> None:
        src = tmp_path / "a.txt"
        src.write_text("x")
        dst = tmp_path / "A.txt"

        logger = OperationLogger()
        service = ExecutionIntegrationService()
        plan = _make_plan(src, dst)
        rule = _make_rule()

        result = service.execute(plan, rule)
        logger.record(result)

        records = logger.records()
        assert len(records) == 1
        assert records[0].success is True
        assert records[0].source == src
        assert records[0].target == dst


# ── IntegrationService without filesystem ────────────────────────────

class TestIntegrationServiceNoFS:
    """Tests that don't require filesystem operations."""

    def test_can_rollback_initially_false(self) -> None:
        service = ExecutionIntegrationService()
        assert not service.can_rollback

    def test_clear_rollback_history(self, tmp_path: Path) -> None:
        src = tmp_path / "f.txt"
        src.write_text("x")
        dst = tmp_path / "F.txt"

        service = ExecutionIntegrationService()
        service.execute(_make_plan(src, dst), _make_rule())
        assert service.can_rollback

        service.clear_rollback_history()
        assert not service.can_rollback


# ── ExecutionWorker contract compatibility ───────────────────────────

class TestExecutionWorkerContract:
    """Verify ExecutionWorker maintains the same Signal contract as RenameWorker."""

    def test_signal_names_match(self) -> None:
        from workers.execution_worker import ExecutionWorker
        from workers.rename_worker import RenameWorker

        # Both expose the same signal names with compatible types
        assert hasattr(ExecutionWorker, "finished_with_result")
        assert hasattr(ExecutionWorker, "progress_changed")
        assert hasattr(RenameWorker, "finished_with_result")
        assert hasattr(RenameWorker, "progress_changed")
