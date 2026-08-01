# ADR-003: Capability Plugin Model

## Status

Accepted (M12-D). Frozen.

## Context

After M12-B established the Plugin Framework and M12-C demonstrated that
an official plugin could implement the contract, the question arose:
should all future plugins follow the same pattern, or could they be ad-hoc?

## Decision

All M12 capability plugins follow a uniform model:

1. **Domain model**: Frozen dataclasses defining the plugin's core concepts
   (e.g., `Policy`, `ValidationRule`, `NotificationChannel`)
2. **Result type**: Frozen dataclass for operation outcomes
   (e.g., `EvaluationResult`, `ValidationResult`, `DeliveryResult`)
3. **Plugin class**: Implements `Plugin` ABC with standard API:
   - `register(obj)` / `unregister(name)`
   - `list_*()` / `get(name)`
   - Domain-specific operations (`validate`, `evaluate`, `notify`, etc.)
   - Convenience methods (`has_failures`, `has_deny`, etc.)
4. **Convenience constructors**: Factory functions for common result patterns
5. **Reference instances**: At least two built-in domain objects demonstrating usage

## Consequences

**Positive:**
- Predictable API surface across all 9 plugins
- Consistent test patterns (metadata, lifecycle, registration, discovery, execution, error handling, independence, integration)
- Onboarding a new plugin follows a known template

**Negative:**
- Uniformity constraint may not fit all future capability types
- Places burden on design to fit the model rather than adapt the model

## Evidence

- All 9 plugins (C-K) follow this model
- Test structure is identical across all plugin test files
- Zero API surprises during the M12 Capability Planning Review
