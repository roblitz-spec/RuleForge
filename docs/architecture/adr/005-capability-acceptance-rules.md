# ADR-005: Capability Acceptance Rules

## Status

Accepted (M12 Closing). Frozen.

## Context

After completing 9 capability plugins (M12-C through M12-K), the M12
Capability Planning Review evaluated 9 hypothetical candidates. All 9
failed to qualify — each was either composable from existing plugins
or belonged in a different architectural layer.

The project needed formal criteria for when a new capability plugin is
justified, to prevent capability proliferation without genuine need.

## Decision

A new official capability plugin is accepted only when it satisfies **all**
six rules:

1. **Cannot be composed from existing capabilities.**
2. **Owns a unique lifecycle responsibility.**
3. **Has a stable public contract.**
4. **Has no responsibility overlap.**
5. **Cannot reasonably belong to Engine / Framework / Rule layer.**
6. **Must implement Plugin ABC only.**

## Consequences

**Positive:**
- Prevents capability dilution
- Forces composition-first thinking
- Preserves architectural clarity
- Guards against scope creep

**Negative:**
- May delay genuinely needed capabilities if misapplied
- Requires discipline to enforce consistently

## Evidence

- M12 Capability Planning Review: 9 candidates evaluated, 0 qualified
- All 9 frozen plugins satisfy these rules retroactively
- The boundary matrix confirms zero overlap among existing plugins
