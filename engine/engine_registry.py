"""EngineRegistry — discover and select ExecutionEngine implementations.

Decouples engine selection from RuleWorkflow.  ExecutionPipeline
remains engine-agnostic — it receives an engine instance, not a name.
"""
from __future__ import annotations

from typing import Type

from engine.execution_engine import ExecutionEngine


class EngineNotFoundError(Exception):
    """Raised when a requested engine name is not registered."""

    def __init__(self, name: str, available: list[str]) -> None:
        self.name = name
        self.available = available
        super().__init__(
            f"Unknown engine '{name}'. Available: {', '.join(available) or '(none)'}"
        )


class DuplicateEngineError(Exception):
    """Raised when attempting to register an already-registered engine name."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(
            f"Engine '{name}' is already registered. Use replace() to overwrite."
        )


class EngineRegistry:
    """Registry of ExecutionEngine factories.

    Usage:
        registry = EngineRegistry.default()
        engine = registry.create("rename")  # new instance each time
        result = ExecutionPipeline.run(context, engine)
    """

    def __init__(self) -> None:
        self._factories: dict[str, Type[ExecutionEngine]] = {}

    # ── Registration ──────────────────────────────────────────────

    def register(self, name: str, engine_cls: Type[ExecutionEngine]) -> None:
        """Register an engine factory.

        Raises DuplicateEngineError if *name* is already registered.
        Use replace() to overwrite.
        """
        if name in self._factories:
            raise DuplicateEngineError(name)
        self._factories[name] = engine_cls

    def replace(self, name: str, engine_cls: Type[ExecutionEngine]) -> None:
        """Register or overwrite an engine factory."""
        self._factories[name] = engine_cls

    # ── Resolution ────────────────────────────────────────────────

    def create(self, name: str) -> ExecutionEngine:
        """Create a new engine instance.

        Always creates a fresh instance — no shared mutable state.

        Raises EngineNotFoundError if *name* is not registered.
        """
        cls = self._factories.get(name)
        if cls is None:
            raise EngineNotFoundError(name, self.names())
        return cls()

    def get_class(self, name: str) -> Type[ExecutionEngine]:
        """Get the registered engine class without instantiating."""
        cls = self._factories.get(name)
        if cls is None:
            raise EngineNotFoundError(name, self.names())
        return cls

    # ── Introspection ─────────────────────────────────────────────

    def names(self) -> list[str]:
        """Return sorted list of registered engine names."""
        return sorted(self._factories.keys())

    def is_registered(self, name: str) -> bool:
        return name in self._factories

    # ── Default registry ──────────────────────────────────────────

    @classmethod
    def default(cls) -> EngineRegistry:
        """Create a registry pre-populated with all built-in engines."""
        from engine.dry_run_execution_engine import DryRunExecutionEngine
        from engine.inspection_execution_engine import InspectionExecutionEngine
        from engine.rename_execution_engine import RenameExecutionEngine
        from engine.string_transform_engine import StringTransformEngine

        r = cls()
        r.register("string", StringTransformEngine)
        r.register("rename", RenameExecutionEngine)
        r.register("dry-run", DryRunExecutionEngine)
        r.register("inspect", InspectionExecutionEngine)
        return r
