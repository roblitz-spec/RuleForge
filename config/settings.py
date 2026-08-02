from __future__ import annotations

import json

from PySide6.QtCore import QSettings

from models.rename_policy import RenamePolicy

_ORGANIZATION = "RuleForge"
_APPLICATION = "RuleForge"
_KEY_POLICY = "rename/policy"
_KEY_LAST_RULE = "rule/last_selected"
_KEY_LAST_PRESET = "preset/last_selected"
_KEY_WORKSPACE_LAST_APP = "workspace/last_app"
_KEY_WORKSPACE_LAST_TASK = "workspace/last_task"
_KEY_WORKSPACE_RECENT_TASKS = "workspace/recent_tasks"


class Settings:
    """应用设置 —— 基于 QSettings，目前仅管理默认重命名策略。"""

    def __init__(self) -> None:
        self._qsettings = QSettings(_ORGANIZATION, _APPLICATION)

    def _init_qsettings(self, qsettings: QSettings) -> None:
        """仅供测试注入自定义 QSettings 实例。"""
        self._qsettings = qsettings

    def get_rename_policy(self) -> RenamePolicy:
        raw = self._qsettings.value(_KEY_POLICY)
        if isinstance(raw, str):
            try:
                return RenamePolicy(raw)
            except ValueError:
                pass
        return RenamePolicy.FAIL

    def set_rename_policy(self, policy: RenamePolicy) -> None:
        self._qsettings.setValue(_KEY_POLICY, policy.value)

    def get_last_rule_id(self) -> str | None:
        raw = self._qsettings.value(_KEY_LAST_RULE)
        return raw if isinstance(raw, str) else None

    def set_last_rule_id(self, rule_id: str) -> None:
        self._qsettings.setValue(_KEY_LAST_RULE, rule_id)

    def get_last_preset_id(self) -> str | None:
        raw = self._qsettings.value(_KEY_LAST_PRESET)
        return raw if isinstance(raw, str) else None

    def set_last_preset_id(self, preset_id: str) -> None:
        self._qsettings.setValue(_KEY_LAST_PRESET, preset_id)

    # ------------------------------------------------------------------
    # Workspace session (M13.4)
    # ------------------------------------------------------------------

    def get_workspace_last_app(self) -> str | None:
        raw = self._qsettings.value(_KEY_WORKSPACE_LAST_APP)
        return raw if isinstance(raw, str) else None

    def set_workspace_last_app(self, app_id: str) -> None:
        self._qsettings.setValue(_KEY_WORKSPACE_LAST_APP, app_id)

    def get_workspace_last_task(self) -> str | None:
        raw = self._qsettings.value(_KEY_WORKSPACE_LAST_TASK)
        return raw if isinstance(raw, str) else None

    def set_workspace_last_task(self, task_title: str) -> None:
        self._qsettings.setValue(_KEY_WORKSPACE_LAST_TASK, task_title)

    def get_workspace_recent_tasks(self) -> list[str]:
        raw = self._qsettings.value(_KEY_WORKSPACE_RECENT_TASKS)
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                pass
        return []

    def set_workspace_recent_tasks(self, tasks: list[str]) -> None:
        self._qsettings.setValue(
            _KEY_WORKSPACE_RECENT_TASKS, json.dumps(tasks))
