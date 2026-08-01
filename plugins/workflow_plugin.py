"""WorkflowPlugin — capability plugin for multi-step workflow orchestration.

Manages registration, discovery, and execution of named workflows.
Each workflow is a sequence of steps; each step invokes a callback.
The plugin coordinates step execution but does NOT execute business
logic — that is delegated to callbacks or the Execution Platform.

Does not modify Execution Platform, Batch Execution, or Plugin
Framework contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


# ── Workflow model ─────────────────────────────────────────────────


@dataclass(frozen=True)
class WorkflowStep:
    """A single step in a workflow.

    Attributes:
        name: Step identifier.
        action: Arbitrary action key (opaque to plugin).
        config: Arbitrary configuration dict (opaque to plugin).
        on_failure: "stop" (default) or "continue" on step error.
    """

    name: str
    action: str
    config: dict = field(default_factory=dict)
    on_failure: str = "stop"

    def __post_init__(self) -> None:
        if self.on_failure not in ("stop", "continue"):
            raise ValueError(
                f"on_failure must be 'stop' or 'continue', got {self.on_failure!r}"
            )


@dataclass(frozen=True)
class Workflow:
    """A named, ordered sequence of steps."""
    name: str
    description: str = ""
    steps: tuple[WorkflowStep, ...] = ()


# ── Result types ───────────────────────────────────────────────────


@dataclass(frozen=True)
class StepResult:
    """Result of executing a single step."""

    step_name: str
    status: str  # "ok" | "failed" | "skipped"
    data: dict = field(default_factory=dict)
    error_message: str = ""


@dataclass(frozen=True)
class WorkflowResult:
    """Result of executing a complete workflow."""

    workflow_name: str
    status: str  # "completed" | "failed" | "partial"
    step_results: tuple[StepResult, ...]
    total_steps: int
    completed_steps: int
    failed_steps: int
    skipped_steps: int

    @property
    def success_rate(self) -> float:
        if self.total_steps == 0:
            return 0.0
        return self.completed_steps / self.total_steps

    @property
    def all_ok(self) -> bool:
        return self.status == "completed" and self.failed_steps == 0

    @property
    def last_error(self) -> str | None:
        for r in reversed(self.step_results):
            if r.status == "failed" and r.error_message:
                return f"{r.step_name}: {r.error_message}"
        return None


# ── Plugin ─────────────────────────────────────────────────────────


class WorkflowPlugin(Plugin):
    """Manages workflow registration, discovery, and execution.

    Usage:
        plugin = WorkflowPlugin()
        registry.register(plugin)
        registry.enable(plugin.name)
        registry.activate(plugin.name)

        step1 = WorkflowStep("validate", action="validate_rule")
        step2 = WorkflowStep("rename", action="execute_rename")
        wf = Workflow("standard", "Standard rename", steps=(step1, step2))
        plugin.register(wf)

        handlers = {
            "validate_rule": lambda ctx: {"valid": True},
            "execute_rename": lambda ctx: {"renamed": 5},
        }
        result = plugin.execute("standard", handlers)

    Capability: EXECUTION_HOOK — workflow execution is an
    execution orchestration concern.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.workflow",
            version="1.0.0",
            description="Manages workflow registration, discovery, and execution",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    def on_activate(self, ctx: PluginContext) -> None:
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        # Preserve workflows on deactivation (Lifecycle vs Business State)
        pass

    # ── Workflow management ────────────────────────────────────

    def register(self, workflow: Workflow) -> None:
        """Register a workflow. Raises ValueError on duplicate name."""
        if workflow.name in self._workflows:
            raise ValueError(
                f"Workflow '{workflow.name}' is already registered"
            )
        self._workflows[workflow.name] = workflow

    def unregister(self, name: str) -> bool:
        """Unregister a workflow by name. Returns True if removed."""
        return self._workflows.pop(name, None) is not None

    def list_workflows(self) -> tuple[Workflow, ...]:
        """Return all registered workflows."""
        return tuple(self._workflows.values())

    def get(self, name: str) -> Workflow | None:
        """Return a workflow by name, or None."""
        return self._workflows.get(name)

    @property
    def workflow_count(self) -> int:
        return len(self._workflows)

    # ── Execution ──────────────────────────────────────────────

    def execute(
        self,
        name: str,
        handlers: dict[str, object],
        context: dict | None = None,
    ) -> WorkflowResult:
        """Execute a registered workflow.

        Args:
            name: Workflow name to execute.
            handlers: Dict mapping action keys to callables.
                Each handler receives ``context`` and returns a dict.
            context: Arbitrary context passed to every handler.

        Returns:
            WorkflowResult with per-step statuses.

        Raises:
            KeyError: Workflow not found.
            KeyError: Handler missing for a step action.
        """
        workflow = self._workflows.get(name)
        if workflow is None:
            raise KeyError(f"Workflow '{name}' not found")

        steps = workflow.steps
        ctx = context or {}
        results: list[StepResult] = []
        completed = 0
        failed = 0
        skipped = 0
        stop = False
        last_action = ""

        for step in steps:
            if stop:
                results.append(StepResult(step.name, "skipped"))
                skipped += 1
                continue

            last_action = step.action

            if step.action not in handlers:
                results.append(
                    StepResult(
                        step.name,
                        status="failed",
                        error_message=f"No handler for action '{step.action}'",
                    )
                )
                failed += 1
                if step.on_failure == "stop":
                    stop = True
                continue

            try:
                handler = handlers[step.action]
                data = handler(ctx)  # type: ignore[operator]
                results.append(
                    StepResult(step.name, status="ok", data=data)
                )
                completed += 1
            except Exception as exc:
                results.append(
                    StepResult(
                        step.name,
                        status="failed",
                        error_message=str(exc),
                    )
                )
                failed += 1
                if step.on_failure == "stop":
                    stop = True

        if failed == 0:
            status = "completed"
        elif completed == 0:
            status = "failed"
        else:
            status = "partial"

        return WorkflowResult(
            workflow_name=workflow.name,
            status=status,
            step_results=tuple(results),
            total_steps=len(steps),
            completed_steps=completed,
            failed_steps=failed,
            skipped_steps=skipped,
        )
