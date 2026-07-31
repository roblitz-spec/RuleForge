from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from models.rule import Rule
from storage.json_storage import JsonStorage


class RuleRepository:
    """规则仓库 —— 管理内存中的 Rule 列表，通过 JsonStorage 持久化。"""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._rules: list[Rule] = []
        self._storage = JsonStorage()

    # ---------- 持久化 ----------

    def load(self) -> None:
        self._rules = self._storage.load_rules(self._path)

    def save(self) -> None:
        self._storage.save_rules(self._path, self._rules)

    # ---------- 查询 ----------

    def all_rules(self) -> list[Rule]:
        """返回排序后的规则列表：pinned 在前，保持原始顺序。"""
        return sorted(self._rules, key=lambda r: (not r.pinned, self._rules.index(r)))

    def find(self, rule_id: str) -> Rule | None:
        for r in self._rules:
            if r.id == rule_id:
                return r
        return None

    # ---------- 修改 ----------

    def add(self, rule: Rule) -> None:
        self._rules.append(rule)

    def update(self, rule: Rule) -> None:
        for i, r in enumerate(self._rules):
            if r.id == rule.id:
                self._rules[i] = rule
                return

    def remove(self, rule_id: str) -> None:
        self._rules = [r for r in self._rules if r.id != rule_id]

    def replace_rules(self, rules: list[Rule]) -> None:
        """替换全部规则（深拷贝）。用于 Preset 加载等批量替换场景。"""
        self._rules = deepcopy(rules)

    # ---------- WP-16: 复制 ----------

    def duplicate(self, rule: Rule) -> Rule:
        """深拷贝规则并赋予唯一 ID，通过 add() 插入仓库。"""
        copy_rule = deepcopy(rule)
        copy_rule.id = self.generate_unique_id()
        copy_rule.name = f"{rule.name} (副本)"
        copy_rule.pinned = False
        self.add(copy_rule)
        return copy_rule

    def generate_unique_id(self) -> str:
        """返回仓库中尚未使用的 `rule_N` 格式 ID。"""
        existing = {r.id for r in self._rules}
        idx = 1
        while f"rule_{idx}" in existing:
            idx += 1
        return f"rule_{idx}"
