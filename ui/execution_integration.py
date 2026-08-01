"""ExecutionIntegrationService — thin adapter between GUI and ExecutionPlatform.

Pure integration: translates GUI requests into ExecutionPipeline calls,
maps results back.  No business logic, no policy decisions, no new
state management beyond what existing components provide.
"""
from __future__ import annotations

from pathlib import Path

from engine.engine_registry import EngineRegistry
from engine.execution_context import ExecutionContext
from engine.execution_pipeline import ExecutionPipeline
from models.rename_plan import RenameAction, RenamePlan, RenamePlanStatus
from models.rename_result import RenameResult
from models.rule import Rule
from plugins.rollback_plugin import RollbackPlugin, RollbackResult


class ExecutionIntegrationService:
    """Translates GUI rename requests into ExecutionPlatform calls.

    Responsibilities (all A/B/C class):
      - Wrap ExecutionPipeline.run() for single-plan execution
      - Map operations_journal → plan.status mutations
      - Map operations_journal → RenameResult for logger compatibility
      - Handle OVERWRITE pre-deletion (mirrors old RenameEngine behavior)
      - Record successful renames to RollbackPlugin
    """

    def __init__(self) -> None:
        self._registry = EngineRegistry.default()
        self._rollback = RollbackPlugin()

    # ── Execution ─────────────────────────────────────────────────

    def execute(self, plan: RenamePlan, rule: Rule) -> RenameResult:
        """Execute a single RenamePlan via ExecutionPipeline.

        Mutates *plan.status* in-place so _on_rename_finished can
        compute success/overwrite/skip/failed counts from plans.
        """
        # Pre-delete target for OVERWRITE (mirrors RenameEngine.rename)
        if plan.action == RenameAction.OVERWRITE and plan.target.exists():
            try:
                plan.target.unlink()
            except OSError as exc:
                plan.status = RenamePlanStatus.FAILED
                plan.message = f"无法覆盖：{exc}"
                return RenameResult(
                    source=plan.source, target=plan.target,
                    success=False, message=plan.message,
                )

        ctx = ExecutionContext(
            rule=rule,
            targets=[str(plan.source)],
        )
        engine = self._registry.create("rename")
        result = ExecutionPipeline.run(ctx, engine)

        journal: list[dict] = result.diagnostics.get("operations_journal", [])  # type: ignore[assignment]
        if not journal:
            plan.status = RenamePlanStatus.FAILED
            plan.message = "执行引擎未返回结果"
            return RenameResult(
                source=plan.source, target=plan.target,
                success=False, message=plan.message,
            )

        op = journal[0]
        if op["status"] == "success":
            if plan.action == RenameAction.OVERWRITE:
                plan.status = RenamePlanStatus.OVERWRITTEN
            else:
                plan.status = RenamePlanStatus.SUCCESS
            self._rollback.record_rename(op["source"], op["target"])
            return RenameResult(
                source=Path(op["source"]),
                target=Path(op["target"]),
                success=True,
            )
        else:
            plan.status = RenamePlanStatus.FAILED
            plan.message = op.get("error") or "未知错误"
            return RenameResult(
                source=Path(op["source"]),
                target=Path(op["target"]),
                success=False,
                message=plan.message,
            )

    # ── Rollback ──────────────────────────────────────────────────

    def rollback(self) -> RollbackResult:
        return self._rollback.rollback()

    @property
    def can_rollback(self) -> bool:
        return self._rollback.history_size > 0

    def clear_rollback_history(self) -> None:
        self._rollback.clear_history()
