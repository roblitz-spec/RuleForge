"""RuleForge Plugin Framework — stable extension mechanism.

Plugins extend RuleForge at defined extension points without modifying
core platform code.  The Plugin Framework is independent of the Execution
Platform (M11) and Batch Execution (M12-A) subsystems.
"""

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext
from plugins.plugin_errors import (
    PluginDependencyError,
    PluginError,
    PluginLifecycleError,
    PluginNotFoundError,
)
from plugins.plugin_registry import PluginRegistry

__all__ = [
    "Plugin",
    "PluginCapability",
    "PluginContext",
    "PluginDependencyError",
    "PluginError",
    "PluginLifecycleError",
    "PluginMetadata",
    "PluginNotFoundError",
    "PluginRegistry",
]
