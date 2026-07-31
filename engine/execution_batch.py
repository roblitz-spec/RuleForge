"""ExecutionBatch — ordered collection of batch execution items.

Each BatchItem is a self-contained execution request: one Rule,
one set of targets, one engine.  BatchExecutor iterates through
them sequentially, running each through ExecutionPipeline.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from models.rule import Rule


@dataclass(frozen=True)
class BatchItem:
    """A single unit of work in a batch execution.

    Fields:
        rule: The committed Rule to execute.
        targets: String inputs or file paths.
        engine_name: Name registered in EngineRegistry (default: "string").
        label: Human-readable identifier for reporting.
        options: Runtime configuration forwarded to ExecutionContext.
    """

    rule: Rule
    targets: list[str]
    engine_name: str = "string"
    label: str = ""
    options: dict[str, object] = field(default_factory=dict)


@dataclass
class ExecutionBatch:
    """Ordered collection of BatchItems with execution policy.

    Fields:
        items: Ordered list of batch items.
        stop_on_error: If True, abort on first failure (remaining items skipped).
        validate_first: If True, pre-validate all items' engines before execution.
    """

    items: list[BatchItem]
    stop_on_error: bool = True
    validate_first: bool = True
