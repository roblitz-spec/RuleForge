"""Tests for M12-G WorkflowPlugin — multi-step workflow orchestration."""

from __future__ import annotations

import pytest

from plugins.plugin_capability import PluginCapability
from plugins.plugin_registry import PluginRegistry
from plugins.workflow_plugin import (
    StepResult,
    Workflow,
    WorkflowPlugin,
    WorkflowResult,
    WorkflowStep,
)


# ── Plugin metadata & lifecycle ───────────────────────────────────


class TestWorkflowPluginMetadata:
    def test_name(self) -> None:
        p = WorkflowPlugin()
        assert p.name == "ruleforge.workflow"

    def test_version(self) -> None:
        p = WorkflowPlugin()
        assert p.version == "1.0.0"

    def test_capability(self) -> None:
        p = WorkflowPlugin()
        assert PluginCapability.EXECUTION_HOOK in p.metadata.capabilities

    def test_dependencies(self) -> None:
        p = WorkflowPlugin()
        assert p.metadata.dependencies == ()


class TestWorkflowPluginLifecycle:
    def test_full_lifecycle_in_registry(self) -> None:
        reg = PluginRegistry()
        reg.register(WorkflowPlugin())
        assert reg.state("ruleforge.workflow") == "LOADED"
        reg.enable("ruleforge.workflow")
        assert reg.state("ruleforge.workflow") == "ENABLED"
        reg.activate("ruleforge.workflow")
        assert reg.state("ruleforge.workflow") == "ACTIVE"
        reg.deactivate("ruleforge.workflow")
        assert reg.state("ruleforge.workflow") == "ENABLED"

    def test_discovery_via_capability(self) -> None:
        reg = PluginRegistry()
        reg.register(WorkflowPlugin())
        reg.enable("ruleforge.workflow")
        plugins = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert any(p.name == "ruleforge.workflow" for p in plugins)

    def test_not_found_when_loaded_only(self) -> None:
        reg = PluginRegistry()
        reg.register(WorkflowPlugin())
        assert reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []

    def test_workflows_persist_after_deactivation(self) -> None:
        reg = PluginRegistry()
        reg.register(WorkflowPlugin())
        reg.enable("ruleforge.workflow")
        reg.activate("ruleforge.workflow")

        plugin = reg.get("ruleforge.workflow")
        assert plugin is not None
        plugin.register(Workflow("wf", steps=(WorkflowStep("s", "a"),)))

        reg.deactivate("ruleforge.workflow")
        assert plugin.workflow_count == 1


# ── Workflow registration ─────────────────────────────────────────


class TestWorkflowRegistration:
    def test_register(self) -> None:
        p = WorkflowPlugin()
        p.register(Workflow("test"))
        assert p.workflow_count == 1

    def test_register_duplicate_raises(self) -> None:
        p = WorkflowPlugin()
        p.register(Workflow("test"))
        with pytest.raises(ValueError, match="already registered"):
            p.register(Workflow("test"))

    def test_unregister(self) -> None:
        p = WorkflowPlugin()
        p.register(Workflow("test"))
        assert p.unregister("test")
        assert p.workflow_count == 0

    def test_unregister_nonexistent_returns_false(self) -> None:
        p = WorkflowPlugin()
        assert p.unregister("nope") is False

    def test_register_multiple(self) -> None:
        p = WorkflowPlugin()
        p.register(Workflow("a"))
        p.register(Workflow("b"))
        p.register(Workflow("c"))
        assert p.workflow_count == 3


# ── Workflow discovery ────────────────────────────────────────────


class TestWorkflowDiscovery:
    def test_list_workflows(self) -> None:
        p = WorkflowPlugin()
        p.register(Workflow("a"))
        p.register(Workflow("b"))
        workflows = p.list_workflows()
        names = {w.name for w in workflows}
        assert names == {"a", "b"}

    def test_list_workflows_empty(self) -> None:
        p = WorkflowPlugin()
        assert p.list_workflows() == ()

    def test_get_workflow(self) -> None:
        p = WorkflowPlugin()
        wf = Workflow("test", "desc", steps=(WorkflowStep("s1", "act"),))
        p.register(wf)
        assert p.get("test") is wf

    def test_get_nonexistent_returns_none(self) -> None:
        p = WorkflowPlugin()
        assert p.get("missing") is None


# ── Workflow execution — success path ─────────────────────────────


class TestWorkflowExecutionSuccess:
    def test_execute_single_step(self) -> None:
        p = WorkflowPlugin()
        step = WorkflowStep("greet", action="greet")
        p.register(Workflow("hello", steps=(step,)))

        result = p.execute("hello", handlers={"greet": lambda ctx: {"msg": "hi"}})
        assert result.status == "completed"
        assert result.total_steps == 1
        assert result.completed_steps == 1
        assert result.failed_steps == 0
        assert result.step_results[0].status == "ok"
        assert result.step_results[0].data == {"msg": "hi"}

    def test_execute_multiple_steps(self) -> None:
        p = WorkflowPlugin()
        steps = (
            WorkflowStep("s1", action="plus_one"),
            WorkflowStep("s2", action="times_two"),
        )
        p.register(Workflow("math", steps=steps))

        handlers = {
            "plus_one": lambda ctx: {"val": ctx.get("x", 0) + 1},
            "times_two": lambda ctx: {"val": ctx.get("x", 0) * 2},
        }
        result = p.execute("math", handlers, context={"x": 3})
        assert result.status == "completed"
        assert result.completed_steps == 2
        assert result.all_ok

    def test_context_passed_to_handlers(self) -> None:
        p = WorkflowPlugin()
        step = WorkflowStep("read", action="read")
        p.register(Workflow("ctx", steps=(step,)))

        result = p.execute(
            "ctx",
            handlers={"read": lambda ctx: {"got": ctx.get("key")}},
            context={"key": "secret"},
        )
        assert result.step_results[0].data == {"got": "secret"}

    def test_execute_nonexistent_workflow_raises(self) -> None:
        p = WorkflowPlugin()
        with pytest.raises(KeyError, match="not found"):
            p.execute("missing", handlers={})


# ── Workflow execution — failure path ─────────────────────────────


class TestWorkflowExecutionFailure:
    def test_missing_handler_fails(self) -> None:
        p = WorkflowPlugin()
        step = WorkflowStep("s1", action="unknown")
        p.register(Workflow("bad", steps=(step,)))

        result = p.execute("bad", handlers={})
        assert result.status == "failed"
        assert result.failed_steps == 1
        assert result.completed_steps == 0
        assert "No handler" in result.step_results[0].error_message

    def test_handler_exception_on_stop(self) -> None:
        p = WorkflowPlugin()
        steps = (
            WorkflowStep("s1", action="fail", on_failure="stop"),
            WorkflowStep("s2", action="ok"),
        )
        p.register(Workflow("stop-wf", steps=steps))

        def _fail(ctx: dict) -> dict:
            raise ValueError("boom")

        result = p.execute(
            "stop-wf",
            handlers={"fail": _fail, "ok": lambda ctx: {"k": "v"}},
        )
        assert result.status == "failed"
        assert result.failed_steps == 1
        assert result.skipped_steps == 1
        assert result.step_results[0].status == "failed"
        assert result.step_results[1].status == "skipped"
        assert "boom" in result.last_error

    def test_handler_exception_on_continue(self) -> None:
        p = WorkflowPlugin()
        steps = (
            WorkflowStep("s1", action="fail", on_failure="continue"),
            WorkflowStep("s2", action="ok"),
        )
        p.register(Workflow("cont-wf", steps=steps))

        def _fail(ctx: dict) -> dict:
            raise RuntimeError("oops")

        result = p.execute(
            "cont-wf",
            handlers={"fail": _fail, "ok": lambda ctx: {"ok": True}},
        )
        assert result.status == "partial"
        assert result.failed_steps == 1
        assert result.completed_steps == 1
        assert result.step_results[0].status == "failed"
        assert result.step_results[1].status == "ok"

    def test_all_steps_fail_with_continue(self) -> None:
        p = WorkflowPlugin()
        steps = (
            WorkflowStep("s1", action="f1", on_failure="continue"),
            WorkflowStep("s2", action="f2", on_failure="continue"),
        )
        p.register(Workflow("all-fail", steps=steps))

        def _fail(ctx: dict) -> dict:
            raise RuntimeError("fail")

        result = p.execute("all-fail", handlers={"f1": _fail, "f2": _fail})
        assert result.status == "failed"
        assert result.failed_steps == 2
        assert result.completed_steps == 0
        assert not result.all_ok


# ── Workflow execution — edge cases ───────────────────────────────


class TestWorkflowExecutionEdgeCases:
    def test_empty_workflow(self) -> None:
        p = WorkflowPlugin()
        p.register(Workflow("empty"))
        result = p.execute("empty", handlers={})
        assert result.status == "completed"
        assert result.total_steps == 0
        assert result.completed_steps == 0
        assert result.all_ok
        assert result.success_rate == 0.0

    def test_context_none_defaults_to_empty(self) -> None:
        p = WorkflowPlugin()
        step = WorkflowStep("s", action="noop")
        p.register(Workflow("def", steps=(step,)))
        result = p.execute("def", handlers={"noop": lambda ctx: {"keys": list(ctx.keys())}})
        assert result.step_results[0].data == {"keys": []}


# ── WorkflowStep ──────────────────────────────────────────────────


class TestWorkflowStep:
    def test_defaults(self) -> None:
        s = WorkflowStep("name", action="act")
        assert s.name == "name"
        assert s.action == "act"
        assert s.config == {}
        assert s.on_failure == "stop"

    def test_invalid_on_failure(self) -> None:
        with pytest.raises(ValueError, match="must be 'stop' or 'continue'"):
            WorkflowStep("x", action="a", on_failure="retry")

    def test_frozen(self) -> None:
        s = WorkflowStep("name", action="act")
        with pytest.raises(Exception):
            s.name = "other"  # type: ignore[misc]


# ── Workflow ──────────────────────────────────────────────────────


class TestWorkflow:
    def test_defaults(self) -> None:
        w = Workflow("name")
        assert w.name == "name"
        assert w.description == ""
        assert w.steps == ()

    def test_frozen(self) -> None:
        w = Workflow("name")
        with pytest.raises(Exception):
            w.name = "other"  # type: ignore[misc]


# ── StepResult ───────────────────────────────────────────────────


class TestStepResult:
    def test_defaults(self) -> None:
        r = StepResult("s", status="ok")
        assert r.step_name == "s"
        assert r.status == "ok"
        assert r.data == {}
        assert r.error_message == ""

    def test_frozen(self) -> None:
        r = StepResult("s", status="ok")
        with pytest.raises(Exception):
            r.status = "failed"  # type: ignore[misc]


# ── WorkflowResult ────────────────────────────────────────────────


class TestWorkflowResult:
    def test_properties(self) -> None:
        wr = WorkflowResult(
            workflow_name="w",
            status="partial",
            step_results=(
                StepResult("s1", "ok"),
                StepResult("s2", "failed", error_message="err"),
                StepResult("s3", "skipped"),
            ),
            total_steps=3,
            completed_steps=1,
            failed_steps=1,
            skipped_steps=1,
        )
        assert wr.success_rate == pytest.approx(1 / 3)
        assert not wr.all_ok
        assert wr.last_error == "s2: err"

    def test_last_error_returns_none_when_no_failure(self) -> None:
        wr = WorkflowResult(
            workflow_name="w",
            status="completed",
            step_results=(StepResult("s1", "ok"),),
            total_steps=1,
            completed_steps=1,
            failed_steps=0,
            skipped_steps=0,
        )
        assert wr.last_error is None

    def test_frozen(self) -> None:
        wr = WorkflowResult(
            workflow_name="w",
            status="completed",
            step_results=(),
            total_steps=0,
            completed_steps=0,
            failed_steps=0,
            skipped_steps=0,
        )
        with pytest.raises(Exception):
            wr.status = "failed"  # type: ignore[misc]


# ── Plugin independence ───────────────────────────────────────────


class TestPluginIndependence:
    def test_no_engine_imports(self) -> None:
        import plugins.workflow_plugin as wp

        source = wp.__file__
        assert source is not None
        with open(source) as f:
            content = f.read()
        assert "from engine" not in content
        assert "import engine" not in content

    def test_standalone_usage_without_registry(self) -> None:
        p = WorkflowPlugin()
        step = WorkflowStep("ping", action="ping")
        p.register(Workflow("standalone", steps=(step,)))
        result = p.execute("standalone", handlers={"ping": lambda ctx: {"pong": True}})
        assert result.all_ok


# ── Full integration flow ─────────────────────────────────────────


class TestFullIntegrationFlow:
    def test_register_discover_execute(self) -> None:
        reg = PluginRegistry()
        reg.register(WorkflowPlugin())
        reg.enable("ruleforge.workflow")
        reg.activate("ruleforge.workflow")

        plugin = reg.get("ruleforge.workflow")
        assert plugin is not None

        # Build reference workflow
        steps = (
            WorkflowStep("validate", action="validate"),
            WorkflowStep("process", action="process"),
            WorkflowStep("notify", action="notify"),
        )
        plugin.register(Workflow("reference", "Reference pipeline", steps=steps))

        # Discover
        wfs = plugin.list_workflows()
        assert len(wfs) == 1
        assert wfs[0].name == "reference"

        # Execute
        handlers = {
            "validate": lambda ctx: {"valid": True},
            "process": lambda ctx: {"items": 42},
            "notify": lambda ctx: {"sent": True},
        }
        result = plugin.execute("reference", handlers)
        assert result.status == "completed"
        assert result.completed_steps == 3
        assert result.failed_steps == 0
        assert result.skipped_steps == 0
        assert result.all_ok
        assert result.success_rate == 1.0
