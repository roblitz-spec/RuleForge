# ADR-004: Zero Cross-Plugin Dependency

## Status

Accepted (M12-D). Enforced through M12-K. Frozen.

## Context

As the number of capability plugins grew, the risk of accidental coupling
increased. If Plugin A imports Plugin B, the architecture loses its
decoupling property: testing becomes harder, freezing becomes interdependent,
and the "single responsibility" principle erodes.

## Decision

Capability plugins must have zero imports from:
- Other capability plugins (cross-plugin imports)
- The engine/ layer (engine imports)
- Any non-framework module

The only allowed imports are:
- `plugins.plugin` (Plugin ABC, PluginMetadata)
- `plugins.plugin_capability` (PluginCapability)
- `plugins.plugin_context` (PluginContext)
- `plugins.plugin_registry` (PluginRegistry — in tests only)
- Python standard library

## Consequences

**Positive:**
- Each plugin is independently testable without any other plugin present
- Freezing one plugin has zero impact on others
- No circular dependency risk
- Architecture remains clean: each plugin is an isolated island

**Negative:**
- Plugins cannot share utility code (must duplicate if needed)
- Composition must happen at the caller level, not within plugins

## Evidence

- Automated import analysis: `grep "from plugins\." plugins/*_plugin.py` → only framework imports
- Automated engine check: `grep "from engine\|import engine"` → 0 matches across all 9 plugins
- Architecture Consistency Review: confirmed 0 cross-plugin imports
