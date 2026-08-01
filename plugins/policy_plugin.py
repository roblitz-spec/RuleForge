"""PolicyPlugin — capability plugin for policy-based decision control.

Manages policy registration, discovery, and evaluation.  Each
policy is a named, callable rule that inspects an evaluation
context and returns a decision.  The plugin evaluates policies
but does NOT execute actions based on them — that is the
caller's responsibility.

Does not modify Execution Platform, Batch Execution, or Plugin
Framework contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


# ── Policy model ──────────────────────────────────────────────────


@dataclass(frozen=True)
class Policy:
    """A named evaluation rule.

    Attributes:
        name: Unique policy identifier.
        description: Human-readable description.
        evaluate: Callable that receives EvaluationContext and
            returns an EvaluationResult.
    """
    name: str
    description: str = ""
    evaluate: Callable = field(default=lambda ctx: evaluation_allow())

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Policy name must not be empty")


# ── Evaluation context ────────────────────────────────────────────


# Type alias for the evaluation context dict.
EvaluationContext = dict


# ── Result types ──────────────────────────────────────────────────


@dataclass(frozen=True)
class EvaluationResult:
    """Outcome of evaluating a single policy.

    Attributes:
        policy_name: Name of the evaluated policy.
        decision: "allow", "deny", or "warn".
        reason: Human-readable explanation.
    """
    policy_name: str
    decision: str  # "allow" | "deny" | "warn"
    reason: str = ""

    def __post_init__(self) -> None:
        if self.decision not in ("allow", "deny", "warn"):
            raise ValueError(
                f"decision must be 'allow', 'deny', or 'warn', "
                f"got {self.decision!r}"
            )

    @property
    def is_allowed(self) -> bool:
        return self.decision == "allow"

    @property
    def is_denied(self) -> bool:
        return self.decision == "deny"

    @property
    def is_warning(self) -> bool:
        return self.decision == "warn"


# ── Convenience constructors ──────────────────────────────────────


def evaluation_allow(reason: str = "") -> EvaluationResult:
    return EvaluationResult(policy_name="", decision="allow", reason=reason)


def evaluation_deny(reason: str = "") -> EvaluationResult:
    return EvaluationResult(policy_name="", decision="deny", reason=reason)


def evaluation_warn(reason: str = "") -> EvaluationResult:
    return EvaluationResult(policy_name="", decision="warn", reason=reason)


# ── Plugin ────────────────────────────────────────────────────────


class PolicyPlugin(Plugin):
    """Manages policy registration, discovery, and evaluation.

    Usage:
        plugin = PolicyPlugin()
        registry.register(plugin)
        registry.enable(plugin.name)
        registry.activate(plugin.name)

        policy = Policy(
            name="max-items",
            description="Limit items to 100",
            evaluate=lambda ctx: (
                evaluation_allow("within limit")
                if ctx.get("count", 0) <= 100
                else evaluation_deny("too many items")
            ),
        )
        plugin.register(policy)

        result = plugin.evaluate("max-items", {"count": 50})
        assert result.is_allowed

    Capability: EXECUTION_HOOK — policy decisions control execution.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.policy",
            version="1.0.0",
            description="Manages policy registration, discovery, and evaluation",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def __init__(self) -> None:
        self._policies: dict[str, Policy] = {}

    def on_activate(self, ctx: PluginContext) -> None:
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        # Preserve policies on deactivation (Lifecycle vs Business State)
        pass

    # ── Registration ───────────────────────────────────────────

    def register(self, policy: Policy) -> None:
        """Register a policy. Raises ValueError on duplicate name."""
        if policy.name in self._policies:
            raise ValueError(
                f"Policy '{policy.name}' is already registered"
            )
        self._policies[policy.name] = policy

    def unregister(self, name: str) -> bool:
        """Unregister a policy by name. Returns True if removed."""
        return self._policies.pop(name, None) is not None

    # ── Discovery ──────────────────────────────────────────────

    def list_policies(self) -> tuple[Policy, ...]:
        """Return all registered policies."""
        return tuple(self._policies.values())

    def get(self, name: str) -> Policy | None:
        """Return a policy by name, or None."""
        return self._policies.get(name)

    @property
    def policy_count(self) -> int:
        return len(self._policies)

    # ── Evaluation ─────────────────────────────────────────────

    def evaluate(
        self,
        name: str,
        context: EvaluationContext | None = None,
    ) -> EvaluationResult:
        """Evaluate a single policy against a context.

        Raises KeyError if the policy is not found.
        """
        policy = self._policies.get(name)
        if policy is None:
            raise KeyError(f"Policy '{name}' not found")
        result = policy.evaluate(context or {})
        # Override policy_name to match the registered name
        return EvaluationResult(
            policy_name=name,
            decision=result.decision,
            reason=result.reason,
        )

    def evaluate_all(
        self,
        context: EvaluationContext | None = None,
    ) -> tuple[EvaluationResult, ...]:
        """Evaluate all registered policies against a context.

        Each policy is evaluated independently.  Results are
        returned in registration order.
        """
        ctx = context or {}
        return tuple(
            EvaluationResult(
                policy_name=p.name,
                decision=(result := p.evaluate(ctx)).decision,
                reason=result.reason,
            )
            for p in self._policies.values()
        )

    def has_deny(
        self,
        context: EvaluationContext | None = None,
    ) -> bool:
        """Check if any policy evaluates to 'deny'."""
        return any(r.is_denied for r in self.evaluate_all(context))
