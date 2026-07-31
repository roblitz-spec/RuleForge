"""CLI — thin presentation layer over RuleWorkflow.

No business logic — every command delegates to RuleWorkflow.
Output is structured for readability; errors produce non-zero
exit codes and clear messages without stack traces.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NoReturn

from engine.rule_workflow import RuleWorkflow

_SEP = "─" * 48
_CHECK = "✓"
_CROSS = "✗"


# ── Output helpers ────────────────────────────────────────────────

def _ok(msg: str) -> None:
    print(f"  {_CHECK} {msg}")


def _fail(msg: str) -> NoReturn:
    print(f"  {_CROSS} {msg}", file=sys.stderr)
    sys.exit(1)


# ── Commands ──────────────────────────────────────────────────────

def cmd_run(examples: str, inputs: str | None = None, name: str = "Inferred Rule") -> None:
    """Full pipeline: infer → validate → preview → commit → execute."""
    pairs = _load_examples(examples)
    if not pairs:
        _fail("No examples provided")

    print(_SEP)
    print(f"  Workflow: {name}")
    print(_SEP)

    wf = RuleWorkflow()
    result = wf.run(pairs, name)

    if not result.success:
        for err in result.errors:
            print(f"  {_CROSS} {err}", file=sys.stderr)
        sys.exit(1)

    if result.inferred_rule is None:
        _fail("Inference produced no rule")

    _ok("Rule inferred")
    step_count = result.inspection.step_count if result.inspection else 0
    print(f"     {step_count} step(s)")

    if result.validation is not None:
        if result.validation.is_valid:
            _ok("Validation succeeded")
        else:
            for msg in result.validation.session_errors:
                print(f"  {_CROSS} {msg}", file=sys.stderr)
            _fail("Validation failed")

    if result.preview is not None:
        _ok("Preview generated")

    _ok("Commit completed")
    _ok("Execution completed")

    print(_SEP)
    print("  Results:")
    if inputs is not None:
        actual_outputs = wf.execute(result.inferred_rule.rule, inputs.split(","))
    else:
        actual_outputs = result.outputs or wf.execute(result.inferred_rule.rule, [o for o, _ in pairs])
    target_inputs = inputs.split(",") if inputs is not None else [o for o, _ in pairs]

    for inp, out in zip(target_inputs, actual_outputs):
        print(f"    {inp}  →  {out}")

    print(_SEP)
    sys.exit(0)


def cmd_infer(examples: str, name: str = "Inferred Rule") -> None:
    """Infer a rule from examples and print as JSON (to stdout).

    Status messages go to stderr so JSON can be piped cleanly.
    """
    pairs = _load_examples(examples)
    if not pairs:
        _fail("No examples provided")

    wf = RuleWorkflow()
    ir = wf.infer(pairs, name)
    if ir is None:
        _fail("Inference produced no rule — examples may be identical")

    print(f"  {_CHECK} Rule inferred", file=sys.stderr)
    print(f"     Name: {ir.rule.name}", file=sys.stderr)
    print(f"     Steps: {len(ir.rule.steps)}", file=sys.stderr)
    print(f"     Lifecycle: {ir.lifecycle.name}", file=sys.stderr)
    print(file=sys.stderr)

    # Serialize rule steps as JSON (stdout only — pipeable)
    steps_data = []
    for step in ir.rule.steps:
        step_dict = {"type": step.type, "id": step.id}
        step_dict.update(step.parameters)
        steps_data.append(step_dict)

    print(json.dumps({"name": ir.rule.name, "steps": steps_data}, indent=2, ensure_ascii=False))
    sys.exit(0)


def cmd_execute(rule_file: str, inputs: list[str]) -> None:
    """Execute a saved rule JSON against string inputs."""
    try:
        data = json.loads(Path(rule_file).read_text())
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        _fail(f"Cannot load rule file: {exc}")

    from models.rule import Rule, RuleStep

    steps = []
    for s in data.get("steps", []):
        params = {k: v for k, v in s.items() if k not in ("type", "id")}
        steps.append(RuleStep(type=s["type"], parameters=params, id=s.get("id", "")))

    rule = Rule(id=data.get("id", "cli-rule"), name=data.get("name", "CLI Rule"), steps=steps)

    wf = RuleWorkflow()
    outputs = wf.execute(rule, list(inputs))

    print(_SEP)
    print(f"  Execute: {rule.name}")
    print(_SEP)
    for inp, out in zip(inputs, outputs):
        print(f"    {inp}  →  {out}")
    print(_SEP)
    _ok("Execution completed")
    sys.exit(0)


# ── Helpers ───────────────────────────────────────────────────────

def _load_examples(raw: str) -> list[tuple[str, str]]:
    """Parse examples from JSON string or file path."""
    # Try as JSON string first
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [(str(a), str(b)) for a, b in parsed]
    except json.JSONDecodeError:
        pass

    # Try as file path
    path = Path(raw)
    if path.is_file():
        data = json.loads(path.read_text())
        if isinstance(data, list):
            return [(str(a), str(b)) for a, b in data]

    return []


# ── Entry point ───────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    """CLI dispatcher — parses args and routes to command handlers."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        _usage()

    # Accept optional "workflow" subcommand prefix
    if argv[0] == "workflow":
        argv = argv[1:]

    if not argv:
        _usage()

    cmd = argv[0]

    if cmd == "run":
        _dispatch_run(argv[1:])
    elif cmd == "infer":
        _dispatch_infer(argv[1:])
    elif cmd == "execute":
        _dispatch_execute(argv[1:])
    elif cmd in ("-h", "--help", "help"):
        _usage()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        _usage(1)


def _dispatch_run(args: list[str]) -> None:
    import argparse
    parser = argparse.ArgumentParser(prog="ruleforge workflow run", description="Run full workflow pipeline")
    parser.add_argument("examples", help="JSON examples: '[[\"a\",\"A\"],...]' or path to JSON file")
    parser.add_argument("--inputs", "-i", default=None, help="Comma-separated inputs for execute (default: use examples)")
    parser.add_argument("--name", "-n", default="Inferred Rule", help="Rule name")
    ns = parser.parse_args(args)
    cmd_run(ns.examples, ns.inputs, ns.name)


def _dispatch_infer(args: list[str]) -> None:
    import argparse
    parser = argparse.ArgumentParser(prog="ruleforge workflow infer", description="Infer rule from examples")
    parser.add_argument("examples", help="JSON examples: '[[\"a\",\"A\"],...]' or path to JSON file")
    parser.add_argument("--name", "-n", default="Inferred Rule", help="Rule name")
    ns = parser.parse_args(args)
    cmd_infer(ns.examples, ns.name)


def _dispatch_execute(args: list[str]) -> None:
    import argparse
    parser = argparse.ArgumentParser(prog="ruleforge workflow execute", description="Execute a rule on inputs")
    parser.add_argument("rule_file", help="Path to rule JSON file")
    parser.add_argument("inputs", nargs="+", help="Input strings to transform")
    ns = parser.parse_args(args)
    cmd_execute(ns.rule_file, ns.inputs)


def _usage(exit_code: int = 0) -> None:
    print("RuleForge — Headless Rule IDE")
    print()
    print("Usage: ruleforge workflow <command> [options]")
    print()
    print("Commands:")
    print("  run       <examples>     Full pipeline: infer → preview → execute")
    print("  infer     <examples>     Infer rule, print as JSON")
    print("  execute   <rule> <inputs>  Execute a saved rule on inputs")
    print()
    print("Examples:")
    print('  ruleforge workflow run \'[["hello","HELLO"],["world","WORLD"]]\'')
    print("  ruleforge workflow infer examples.json --name Upper")
    print("  ruleforge workflow execute rule.json hello world")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
