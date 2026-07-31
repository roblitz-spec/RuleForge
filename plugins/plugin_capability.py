"""PluginCapability — declared capabilities a plugin provides."""

from __future__ import annotations

from enum import Enum


class PluginCapability(Enum):
    """Capabilities a plugin can declare.

    The registry uses these for targeted queries via
    ``list_by_capability()``.  Each capability corresponds to a
    defined extension point in the platform.

    Values are stable — do not rename or reorder without a
    migration plan.
    """

    RULE_DISCOVERY = "rule_discovery"
    VALIDATION = "validation"
    EXECUTION_HOOK = "execution_hook"
    BATCH_HOOK = "batch_hook"
    RESULT_PROCESSING = "result_processing"
    OUTPUT_EXPORT = "output_export"
