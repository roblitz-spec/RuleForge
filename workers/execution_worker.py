"""ExecutionWorker — QThread wrapper for ExecutionIntegrationService.

Replaces RenameWorker: executes plans via ExecutionPipeline instead
of the old RenameEngine, while preserving the same Signal contract.
"""
from __future__ import annotations

import sys

from PySide6.QtCore import QThread, Signal

from engine.operation_logger import OperationLogger
from models.rename_plan import RenameAction, RenamePlan
from models.rule import Rule
from ui.execution_integration import ExecutionIntegrationService


class ExecutionWorker(QThread):
    """Background execution thread — calls ExecutionPipeline per plan.

    Emits progress_changed(int current, int total) after each plan
    and finished_with_result(list[RenameResult]) when done.

    Signal contract is identical to RenameWorker so MainWindow
    needs minimal changes.
    """

    finished_with_result = Signal(list)
    progress_changed = Signal(int, int)

    def __init__(
        self,
        plans: list[RenamePlan],
        rule: Rule,
        integration: ExecutionIntegrationService,
        logger: OperationLogger | None = None,
        parent: QThread | None = None,
    ) -> None:
        super().__init__(parent)
        self._plans = plans
        self._rule = rule
        self._integration = integration
        self._logger = logger

    def run(self) -> None:
        total = len(self._plans)
        results: list = []
        try:
            for i, plan in enumerate(self._plans):
                if plan.action in (RenameAction.RENAME, RenameAction.OVERWRITE):
                    rr = self._integration.execute(plan, self._rule)
                else:
                    from models.rename_result import RenameResult
                    rr = RenameResult(
                        source=plan.source, target=plan.target,
                        success=True, message=plan.message or "已跳过",
                    )
                results.append(rr)
                if self._logger is not None:
                    self._logger.record(rr)
                self.progress_changed.emit(i + 1, total)
        except Exception as e:
            print(f"[ExecutionWorker] Error during execution: {e}", file=sys.stderr)
        self.finished_with_result.emit(results)
