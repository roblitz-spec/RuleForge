"""M11-B: RenameExecutionEngine tests.

Covers successful execution, conflict detection, fail-fast behavior,
and ExecutionPipeline integration.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from models.rule import Rule, RuleStep
from engine.execution_context import ExecutionContext
from engine.execution_pipeline import ExecutionPipeline
from engine.execution_result import ExecutionResult
from engine.filesystem_adapter import FilesystemAdapter, RealFilesystemAdapter
from engine.rename_execution_engine import RenameExecutionEngine
from engine.rule_workflow import RuleWorkflow


def _make_rule() -> Rule:
    """Lowercase → Uppercase rule."""
    return Rule(
        id="test-rename",
        name="ToUpper",
        steps=[RuleStep(type="case", parameters={"mode": "upper"})],
    )


def _make_files(parent: str, *names: str) -> list[str]:
    """Create empty files in parent directory, return full paths."""
    paths = []
    for name in names:
        p = str(Path(parent) / name)
        Path(p).write_text("")
        paths.append(p)
    return paths


# ── Successful execution ──────────────────────────────────────────

class TestRenameExecutionSuccess:
    def test_single_rename(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "hello.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            engine = RenameExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is True
            assert result.actions_executed == 1
            assert result.actions_skipped == 0

            # Verify file was renamed
            assert not Path(src).exists()
            assert Path(td, "HELLO.txt").exists()

    def test_multiple_renames(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "a.txt", "b.txt", "c.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = RenameExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is True
            assert result.actions_executed == 3
            assert Path(td, "A.txt").exists()
            assert Path(td, "B.txt").exists()
            assert Path(td, "C.txt").exists()

    def test_no_change_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "ALREADY.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            engine = RenameExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is True
            assert result.actions_executed == 0
            assert result.actions_skipped == 1

    def test_deterministic_order(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "z.txt", "a.txt", "m.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[srcs[1], srcs[0], srcs[2]])
            engine = RenameExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is True
            journal = result.diagnostics["operations_journal"]
            sources = [e["source"] for e in journal]
            # Should be sorted by source path
            assert sources == sorted(sources)

    def test_journal_present(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "test.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            engine = RenameExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            journal = result.diagnostics.get("operations_journal", [])
            assert len(journal) == 1
            assert journal[0]["status"] == "success"
            assert journal[0]["source"] == src
            assert journal[0]["target"] == str(Path(td) / "TEST.txt")


# ── Conflict detection ────────────────────────────────────────────

class TestConflictDetection:
    def test_duplicate_targets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            # "hello.txt" → "HELLO.txt", "Hello.txt" → "HELLO.txt" (case collision)
            srcs = _make_files(td, "hello.txt", "Hello.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = RenameExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is False
            assert any("Duplicate target" in e for e in result.errors)
            # Neither file should have been renamed
            assert Path(td, "hello.txt").exists()
            assert Path(td, "Hello.txt").exists()

    def test_destination_exists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "hello.txt")[0]
            existing = _make_files(td, "HELLO.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            engine = RenameExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is False
            assert any("already exists" in e.lower() for e in result.errors)
            # Source should not have been renamed
            assert Path(src).exists()

    def test_missing_source(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["/nonexistent/path.txt"])
        engine = RenameExecutionEngine()

        result = ExecutionPipeline.run(ctx, engine)
        assert result.success is False
        assert any("do not exist" in e for e in result.errors)


# ── Fail-fast ─────────────────────────────────────────────────────

class TestFailFast:
    def test_stops_on_first_failure(self) -> None:
        """Use a custom adapter that fails on the second file."""
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "a.txt", "b.txt", "c.txt")
            rule = _make_rule()

            call_count = [0]

            class FailingAdapter(RealFilesystemAdapter):
                def rename(self, src, dst):
                    call_count[0] += 1
                    if call_count[0] == 2:
                        msg = "Permission denied"
                        raise PermissionError(msg)
                    super().rename(src, dst)

            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = RenameExecutionEngine(fs=FailingAdapter())

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is False
            assert result.actions_executed == 1  # only a.txt renamed
            assert not Path(srcs[0]).exists()  # was renamed
            assert Path(srcs[2]).exists()  # c.txt untouched (fail-fast)


# ── Pipeline integration ──────────────────────────────────────────

class TestPipelineIntegration:
    def test_via_execution_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "test.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            engine = RenameExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert isinstance(result, ExecutionResult)
            assert result.success is True
            assert result.duration_ms is not None

    def test_via_rule_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "hello.txt")[0]
            rule = _make_rule()

            result = RuleWorkflow.execute_with_engine(
                rule, [src], engine=RenameExecutionEngine(),
            )
            assert result.success is True
            assert not Path(src).exists()
            assert Path(td, "HELLO.txt").exists()

    def test_cleanup_runs_after_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "dup.txt", "dup.txt")  # same name twice
            # Actually need a case where targets collide
            srcs2 = _make_files(td, "hello.txt")
            srcs3 = _make_files(td, "Hello.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs2 + srcs3)
            engine = RenameExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is False
            # After cleanup, internal state should be clear
            assert engine._ops == []
            assert engine._conflicts == []

    def test_session_lifecycle_unchanged(self) -> None:
        """Verify RenameExecutionEngine does not touch RuleSession."""
        wf = RuleWorkflow()
        ir = wf.infer([("hello", "HELLO"), ("world", "WORLD")])
        assert ir is not None

        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "hello.txt")[0]
            result = wf.execute_with_engine(
                ir.rule, [src], engine=RenameExecutionEngine(),
            )
            assert result.success is True

        # Session state should be unchanged (no session was opened)
        # Just verify we can still use the workflow
        ir2 = wf.infer([("a", "A")])
        assert ir2 is not None
