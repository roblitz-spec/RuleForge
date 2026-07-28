from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class RuleStep:
    """重命名规则中的一个步骤。"""

    type: str
    parameters: dict[str, object] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
