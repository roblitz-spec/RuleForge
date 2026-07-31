"""Plugin error types — explicit, catchable, never silent."""

from __future__ import annotations


class PluginError(Exception):
    """Base class for all plugin-related errors."""


class PluginNotFoundError(PluginError):
    """A requested plugin is not registered."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Plugin '{name}' is not registered")


class PluginLifecycleError(PluginError):
    """A lifecycle transition failed or is invalid.

    The plugin's state is unchanged after this error.
    """

    def __init__(self, name: str, state: str, transition: str) -> None:
        self.name = name
        self.state = state
        self.transition = transition
        super().__init__(
            f"Plugin '{name}' in state '{state}' cannot transition to '{transition}'"
        )


class PluginDependencyError(PluginError):
    """A plugin dependency is missing or circular."""

    def __init__(self, name: str, dependency: str) -> None:
        self.name = name
        self.dependency = dependency
        super().__init__(
            f"Plugin '{name}' depends on '{dependency}' which is not available"
        )
