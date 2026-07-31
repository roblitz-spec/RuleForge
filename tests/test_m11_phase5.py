"""M11-E: Execution Observability & Diagnostics tests.

Covers trace, metrics, diagnostics, pipeline instrumentation,
backward compatibility, and engine-agnostic output.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from models.rule import Rule, RuleStep
from engine.execution_context import ExecutionContext
from engine.execution_diagnostics import ExecutionDiagnostics
from engine.execution_metrics import ExecutionMetrics
from engine.execution_pipeline import ExecutionPipeline
from engine.execution_result import ExecutionResult
from engine.execution_trace import ExecutionTrace, TraceEvent
from engine.dry_run_execution_engine import DryRunExecutionEngine
from engine.inspection_execution_engine import InspectionExecutionEngine
from engine.rename_execution_engine import RenameExecutionEngine
from engine.string_transform_engine import StringTransformEngine
from engine.rule_workflow import RuleWorkflow


def _make_rule() -> Rule:
    return Rule(
        id="test-obs",
        name="ToUpper",
        steps=[RuleStep(type="case", parameters={"mode": "upper"})],
    )


def _make_files(parent: str, *names: str) -> list[str]:
    paths = []
    for name in names:
        p = str(Path(parent) / name)
        Path(p).write_text("")
        paths.append(p)
    return paths


# ── ExecutionTrace ────────────────────────────────────────────────

class TestExecutionTrace:
    def test_creates_execution_id(self) -> None:
        t = ExecutionTrace()
        assert t.execution_id.startswith("exec_")
        assert len(t.execution_id) == 17  # "exec_" + 12 hex chars

    def test_lifecycle_order(self) -> None:
        t = ExecutionTrace()
        t.start("TestEngine")
        t_prep = t.stage_started("prepare")
        t.stage_completed("prepare", t_prep)
        t_exec = t.stage_started("execute")
        t.stage_completed("execute", t_exec)
        t_clean = t.stage_started("cleanup")
        t.stage_completed("cleanup", t_clean)
        t.finish()

        event_types = [e.event_type for e in t.events]
        assert event_types == [
            "execution.started",
            "prepare.started",
            "prepare.completed",
            "execute.started",
            "execute.completed",
            "cleanup.started",
            "cleanup.completed",
            "execution.finished",
        ]

    def test_duration_recorded(self) -> None:
        t = ExecutionTrace()
        t.start("E")
        t_prep = t.stage_started("prepare")
        t.stage_completed("prepare", t_prep)
        t.finish()
        assert t.duration_ms >= 0

    def test_stage_duration_in_event(self) -> None:
        t = ExecutionTrace()
        t.start("E")
        t_prep = t.stage_started("prepare")
        t.stage_completed("prepare", t_prep)
        complete_evts = [e for e in t.events if e.event_type.endswith(".completed")]
        for e in complete_evts:
            assert e.duration_ms is not None
            assert e.duration_ms >= 0

    def test_engine_name_recorded(self) -> None:
        t = ExecutionTrace()
        t.start("TestEngine")
        assert t.engine_name == "TestEngine"

    def test_to_dict(self) -> None:
        t = ExecutionTrace()
        t.start("TestEngine")
        t.finish()
        d = t.to_dict()
        assert d["engine_name"] == "TestEngine"
        assert "events" in d
        assert "duration_ms" in d


# ── ExecutionMetrics ──────────────────────────────────────────────

class TestExecutionMetrics:
    def test_defaults(self) -> None:
        m = ExecutionMetrics()
        assert m.files_scanned == 0
        assert m.files_modified == 0
        assert m.files_skipped == 0

    def test_extra_extension(self) -> None:
        m = ExecutionMetrics(extra={"would_modify_count": 5})
        assert m.extra["would_modify_count"] == 5

    def test_to_dict_includes_extra(self) -> None:
        m = ExecutionMetrics(
            files_modified=3,
            files_skipped=1,
            extra={"would_rename": 3},
        )
        d = m.to_dict()
        assert d["files_modified"] == 3
        assert d["files_skipped"] == 1
        assert d["would_rename"] == 3


# ── ExecutionDiagnostics ──────────────────────────────────────────

class TestExecutionDiagnostics:
    def test_structured_fields(self) -> None:
        d = ExecutionDiagnostics()
        d.add_error("oops")
        d.add_warning("heads up")
        d.add_conflict("dup target")
        d.add_journal_entry({"src": "a.txt", "dst": "A.txt"})
        assert d.errors == ["oops"]
        assert d.warnings == ["heads up"]
        assert d.conflicts == ["dup target"]
        assert d.journal == [{"src": "a.txt", "dst": "A.txt"}]

    def test_to_dict_omits_empty(self) -> None:
        d = ExecutionDiagnostics()
        assert d.to_dict() == {}

    def test_to_dict_includes_populated(self) -> None:
        d = ExecutionDiagnostics(metadata={"mode": "dry_run"})
        d.add_error("err")
        result = d.to_dict()
        assert result["errors"] == ["err"]
        assert result["metadata"] == {"mode": "dry_run"}


# ── Pipeline instrumentation ──────────────────────────────────────

class TestPipelineInstrumentation:
    def test_trace_present_on_result(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "x.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])

            result = ExecutionPipeline.run(ctx, RenameExecutionEngine())
            assert result.trace is not None
            assert isinstance(result.trace, ExecutionTrace)
            assert result.trace.engine_name == "RenameExecutionEngine"

    def test_metrics_present_on_result(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "y.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])

            result = ExecutionPipeline.run(ctx, RenameExecutionEngine())
            assert result.metrics is not None
            assert isinstance(result.metrics, ExecutionMetrics)
            assert result.metrics.files_modified == 1

    def test_lifecycle_order_correct(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "a.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])

            result = ExecutionPipeline.run(ctx, RenameExecutionEngine())
            events = result.trace.events
            stages = [e.stage for e in events]
            expected_order = [
                "execution", "prepare", "prepare",
                "execute", "execute",
                "cleanup", "cleanup",
                "execution",
            ]
            assert stages == expected_order, f"got: {stages}"

    def test_cleanup_always_recorded_in_trace(self) -> None:
        """Cleanup appears in trace even when execute fails."""
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "good.txt")[0]
            # Will fail on duplicate targets
            srcs = [src, src]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)

            result = ExecutionPipeline.run(ctx, DryRunExecutionEngine())
            stage_names = {e.stage for e in result.trace.events}
            assert "cleanup" in stage_names

    def test_failure_trace_preserved(self) -> None:
        """Even on prepare failure, trace is populated."""
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["/nonexistent/x.txt"])
        result = ExecutionPipeline.run(ctx, RenameExecutionEngine())
        assert result.trace is not None
        assert result.metrics is not None
        assert result.metrics.error_count >= 1
        # Cleanup still recorded
        stage_names = {e.stage for e in result.trace.events}
        assert "cleanup" in stage_names

    def test_prepare_failure_trace_preserved(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["/nonexistent/x.txt"])
        result = ExecutionPipeline.run(ctx, RenameExecutionEngine())
        assert result.trace is not None
        assert result.metrics is not None

    # ── All engines produce traces ──────────────────────────────

    def test_string_engine_produces_trace(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["hello"])
        result = ExecutionPipeline.run(ctx, StringTransformEngine())
        assert result.trace is not None
        assert result.metrics is not None

    def test_dry_run_produces_trace(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "x.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            result = ExecutionPipeline.run(ctx, DryRunExecutionEngine())
            assert result.trace is not None
            assert result.trace.engine_name == "DryRunExecutionEngine"

    def test_inspection_produces_trace(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "z.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            result = ExecutionPipeline.run(ctx, InspectionExecutionEngine())
            assert result.trace is not None
            assert result.trace.engine_name == "InspectionExecutionEngine"


# ── Backward compatibility ────────────────────────────────────────

class TestBackwardCompat:
    def test_execution_result_works_without_trace(self) -> None:
        """Manual ExecutionResult still works without trace/metrics."""
        r = ExecutionResult(
            success=True,
            outputs=["HELLO"],
            actions_executed=1,
            diagnostics={"mode": "manual"},
        )
        assert r.success is True
        assert r.trace is None
        assert r.metrics is None
        assert r.diagnostics["mode"] == "manual"
        assert r.duration_ms is None

    def test_existing_diagnostics_still_accessible(self) -> None:
        """Old pattern: result.diagnostics dict still works."""
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "x.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])

            result = ExecutionPipeline.run(ctx, DryRunExecutionEngine())
            assert isinstance(result.diagnostics, dict)
            assert "mode" in result.diagnostics
            assert result.diagnostics["mode"] == "dry_run"

    def test_execute_returns_list_still_works(self) -> None:
        rule = _make_rule()
        outputs = RuleWorkflow.execute(rule, ["hello"])
        assert outputs == ["HELLO"]

    def test_execute_with_engine_still_works(self) -> None:
        rule = _make_rule()
        result = RuleWorkflow.execute_with_engine(
            rule, ["hello"], engine=StringTransformEngine(),
        )
        assert result.success is True
        # New fields just appear — don't break existing code
        assert result.trace is not None

    def test_execute_named_still_works(self) -> None:
        rule = _make_rule()
        result = RuleWorkflow.execute_named(rule, ["a"], engine_name="string")
        assert result.success is True
        assert result.trace is not None
        assert result.metrics is not None


# ── DryRun metrics ────────────────────────────────────────────────

class TestDryRunMetrics:
    def test_would_modify_count(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "a.txt", "b.txt", "C.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            result = ExecutionPipeline.run(ctx, DryRunExecutionEngine())
            assert result.metrics is not None
            assert result.metrics.files_modified == 2  # a+b renamed, C skipped
            assert result.metrics.files_skipped == 1


# ── Inspection metrics ────────────────────────────────────────────

class TestInspectionMetrics:
    def test_metadata_count(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            _make_files(td, *[f"f{i}.txt" for i in range(5)])
            srcs = [str(p) for p in Path(td).iterdir()]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)

            result = ExecutionPipeline.run(ctx, InspectionExecutionEngine())
            assert result.metrics is not None
            assert result.metrics.files_selected == 5
            assert result.metrics.files_modified == 5
            assert result.metrics.files_skipped == 0
