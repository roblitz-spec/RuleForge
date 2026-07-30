"""RuleWorkflow — orchestration layer for the complete Rule lifecycle.

Composes existing capabilities (RuleInference, RuleSession,
RuleInspector, preview_pipeline) without owning state or
introducing new domain logic.

RuleSession remains the authoritative mutable object.

Designed as a single entry point for CLI, SDK, API, and GUI.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.preview_pipeline import preview_rule
from engine.rule_inference import infer_rule
from engine.rule_inspector import RuleInspection
from engine.rule_session import RuleSession
from models.inferred_rule import InferredRule
from models.rule import Rule
from models.session_validation import SessionValidationResult


@dataclass
class WorkflowResult:
    """Result of a RuleWorkflow pipeline run.

    Captures the outcome at each stage.  Errors are collected
    rather than raised — callers inspect `success` and `errors`.
    """

    inferred_rule: InferredRule | None = None
    inspection: RuleInspection | None = None
    validation: SessionValidationResult | None = None
    preview: object | None = None  # ExamplePreviewResult (lazy import)
    outputs: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    success: bool = True

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.success = False


class RuleWorkflow:
    """Orchestrates the complete Rule lifecycle.

    Pure orchestration — every method delegates to an existing
    component.  No domain logic, no state ownership, no
    persistence.

    Usage:
        wf = RuleWorkflow()

        # Step by step
        ir = wf.infer([("hello", "HELLO")])
        session = wf.open_session(ir)
        info = wf.inspect(session.rule)
        session.edit_step(step_id, "mode", "lower")
        result = session.validate()
        preview = session.preview()
        session.commit()
        outputs = wf.execute(session.rule, ["world"])

        # Or full pipeline
        result = wf.run([("hello", "HELLO"), ("world", "WORLD")])
    """

    # ── Stage methods (stateless — delegate to existing modules) ──

    @staticmethod
    def infer(
        examples: list[tuple[str, str]],
        name: str = "Inferred Rule",
    ) -> InferredRule | None:
        """Infer a Rule from example pairs.

        Returns None if no transformation is needed or inference fails.
        """
        return infer_rule(examples, name)

    @staticmethod
    def open_session(
        inferred_rule: InferredRule,
        store: object | None = None,
    ) -> RuleSession:
        """Open a RuleSession for an InferredRule.

        The caller owns the session — close it when done.
        """
        session = RuleSession()
        session.open(inferred_rule, store)  # type: ignore[arg-type]
        return session

    @staticmethod
    def inspect(rule: Rule) -> RuleInspection:
        """Produce a structured inspection of a Rule."""
        return RuleInspection.inspect(rule)

    @staticmethod
    def execute(rule: Rule, inputs: list[str]) -> list[str]:
        """Apply a committed Rule to string inputs.

        Returns the transformed outputs.  This is the headless
        execution path — no filesystem access, no adapters.
        """
        result = preview_rule(rule, inputs)
        return [e.output_text for e in result.entries]

    # ── Full pipeline ───────────────────────────────────────────

    def run(
        self,
        examples: list[tuple[str, str]],
        name: str = "Inferred Rule",
        store: object | None = None,
    ) -> WorkflowResult:
        """Run the complete workflow: infer → inspect → preview → execute.

        Opens and closes a RuleSession internally.  For interactive
        editing, use the stage methods directly.

        Args:
            examples: List of (original, desired) pairs.
            name: Human-readable name for the inferred rule.
            store: Optional InferredRuleStore for persistence.

        Returns:
            WorkflowResult with outcomes at each stage.
        """
        result = WorkflowResult()

        # 1. Infer
        ir = self.infer(examples, name)
        if ir is None:
            result.add_error("Inference produced no rule — examples may be identical")
            return result
        result.inferred_rule = ir

        # 2. Inspect
        result.inspection = self.inspect(ir.rule)

        # 3. Open session → validate → preview → commit
        session = self.open_session(ir, store)
        try:
            result.validation = session.validate()
            if not result.validation.is_valid:
                for msg in result.validation.session_errors:
                    result.add_error(f"Validation: {msg}")

            result.preview = session.preview()
            session.commit()
            session.finalize()
        finally:
            session.close()

        # 4. Execute
        originals = [o for o, _ in examples]
        try:
            result.outputs = self.execute(ir.rule, originals)
        except Exception as exc:
            result.add_error(f"Execution failed: {exc}")

        return result
