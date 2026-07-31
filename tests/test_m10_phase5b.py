"""M10.5-D: CLI integration tests.

Tests the CLI as a thin wrapper over RuleWorkflow — no
direct manipulation of RuleSession or internal components.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

CLI = [sys.executable, "-m", "cli.workflow_cli"]

EXAMPLES_JSON = '[["hello","HELLO"],["world","WORLD"]]'
EXAMPLES_NO_CHANGE = '[["hello","hello"],["world","world"]]'


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*CLI, *args],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )


# ── Help ──────────────────────────────────────────────────────────

class TestCLIHelp:
    def test_help_no_args(self) -> None:
        r = _run()
        assert r.returncode == 0
        assert "RuleForge" in r.stdout
        assert "workflow" in r.stdout

    def test_help_flag(self) -> None:
        r = _run("--help")
        assert r.returncode == 0
        assert "Usage:" in r.stdout

    def test_unknown_command(self) -> None:
        r = _run("foo")
        assert r.returncode == 1
        assert "Unknown command" in r.stderr


# ── Run command ───────────────────────────────────────────────────

class TestCLIRun:
    def test_run_full_pipeline_success(self) -> None:
        r = _run("workflow", "run", EXAMPLES_JSON, "-n", "TestRun")
        assert r.returncode == 0
        assert "Rule inferred" in r.stdout
        assert "Validation succeeded" in r.stdout
        assert "Commit completed" in r.stdout
        assert "Execution completed" in r.stdout
        assert "hello  →  HELLO" in r.stdout
        assert "world  →  WORLD" in r.stdout

    def test_run_no_change_examples(self) -> None:
        """Inference with identical input/output should fail gracefully."""
        r = _run("workflow", "run", EXAMPLES_NO_CHANGE, "-n", "NoChange")
        assert r.returncode == 1

    def test_run_invalid_json(self) -> None:
        r = _run("workflow", "run", "not-json", "-n", "BadJSON")
        assert r.returncode == 1
        assert "No examples" in r.stderr

    def test_run_with_custom_inputs(self) -> None:
        r = _run(
            "workflow", "run", EXAMPLES_JSON,
            "-n", "CI", "--inputs", "foo,bar",
        )
        assert r.returncode == 0
        assert "foo  →  FOO" in r.stdout
        assert "bar  →  BAR" in r.stdout

    def test_run_output_format(self) -> None:
        """Verify consistent output structure."""
        r = _run("workflow", "run", EXAMPLES_JSON, "-n", "Fmt")
        assert r.returncode == 0
        assert "────────────────" in r.stdout
        assert "Workflow:" in r.stdout
        assert "Results:" in r.stdout


# ── Infer command ─────────────────────────────────────────────────

class TestCLIInfer:
    def test_infer_produces_valid_json(self) -> None:
        r = _run("workflow", "infer", EXAMPLES_JSON, "-n", "Upper")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["name"] == "Upper"
        assert len(data["steps"]) >= 1

    def test_infer_status_to_stderr(self) -> None:
        """Status messages go to stderr, JSON to stdout."""
        r = _run("workflow", "infer", EXAMPLES_JSON, "-n", "Upper")
        assert r.returncode == 0
        assert "Rule inferred" in r.stderr
        # stdout is pure JSON (indented, so starts with {)
        assert r.stdout.strip().startswith("{")


# ── Execute command ───────────────────────────────────────────────

class TestCLIExecute:
    @pytest.fixture
    def rule_file(self, tmp_path: Path) -> str:
        """Create a temporary rule JSON file."""
        data = {
            "name": "Upper",
            "steps": [{"type": "case", "id": "step1", "mode": "upper"}],
        }
        path = tmp_path / "rule.json"
        path.write_text(json.dumps(data))
        return str(path)

    def test_execute_rule_from_file(self, rule_file: str) -> None:
        r = _run("workflow", "execute", rule_file, "hello", "world", "TEST")
        assert r.returncode == 0
        assert "hello  →  HELLO" in r.stdout
        assert "world  →  WORLD" in r.stdout
        assert "TEST  →  TEST" in r.stdout

    def test_execute_missing_file(self) -> None:
        r = _run("workflow", "execute", "/nonexistent/rule.json", "hello")
        assert r.returncode == 1
        assert "Cannot load rule file" in r.stderr

    def test_execute_invalid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("not json")
        r = _run("workflow", "execute", str(path), "hello")
        assert r.returncode == 1
        assert "Cannot load rule file" in r.stderr


# ── Exit code behavior ────────────────────────────────────────────

class TestCLIExitCodes:
    def test_success_exit_zero(self) -> None:
        r = _run("workflow", "run", EXAMPLES_JSON, "-n", "Exit")
        assert r.returncode == 0

    def test_failure_exit_nonzero(self) -> None:
        r = _run("workflow", "run", EXAMPLES_NO_CHANGE, "-n", "Fail")
        assert r.returncode != 0

    def test_invalid_command_exit_nonzero(self) -> None:
        r = _run("badcommand")
        assert r.returncode != 0

    def test_infer_success_exit_zero(self) -> None:
        r = _run("workflow", "infer", EXAMPLES_JSON, "-n", "Exit")
        assert r.returncode == 0


# ── Roundtrip: infer → execute ────────────────────────────────────

class TestCLIRoundtrip:
    def test_infer_to_execute(self, tmp_path: Path) -> None:
        """Infer a rule, save to file, execute it."""
        # 1. Infer
        r_infer = _run("workflow", "infer", EXAMPLES_JSON, "-n", "Upper")
        assert r_infer.returncode == 0

        rule_path = tmp_path / "rule.json"
        rule_path.write_text(r_infer.stdout)

        # 2. Execute
        r_exec = _run("workflow", "execute", str(rule_path), "hello", "foo")
        assert r_exec.returncode == 0
        assert "hello  →  HELLO" in r_exec.stdout
        assert "foo  →  FOO" in r_exec.stdout
