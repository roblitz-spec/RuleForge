"""PluginContext — read-only context for plugin lifecycle callbacks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plugins.plugin_registry import PluginRegistry


@dataclass(frozen=True)
class PluginContext:
    """Immutable context passed to plugin lifecycle hooks.

    Fields:
        registry: Reference to the PluginRegistry for inter-plugin
                  communication and capability queries.
        data: Opaque key-value store for host→plugin and
              plugin→plugin data sharing.
    """

    registry: PluginRegistry | None = None
    data: dict[str, object] = field(default_factory=dict)
