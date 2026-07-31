from __future__ import annotations

from dataclasses import dataclass, field

from models.rule import Rule


@dataclass
class Preset:
    """命名的规则集合 — 持久化模板，非运行时状态。"""

    id: str
    name: str
    description: str = ""
    rules: list[Rule] = field(default_factory=list)
    version: int = 1
