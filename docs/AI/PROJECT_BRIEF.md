# RuleForge — Project Brief

> **Product Direction**: AI-assisted Rule IDE. ResourceHub was the origin — batch file rename is the initial adapter/use case. The core value proposition is: Example → Rule Inference → Rule → Test/Preview → Execute → Reuse.

## What

RuleForge is an AI-assisted Rule IDE. Given transformation examples (original → desired), it infers candidate rules, lets users refine and test them, and executes transformations reliably. Initial adapter: batch file rename. Built with Python 3.12+ and PySide6.

## Product Hierarchy

| Layer | Component | Status |
|---|---|---|
| Product | AI-assisted Rule IDE | M10 (next) |
| Core Intelligence | RuleInference Engine (M9) | ✅ Complete |
| Core | Rule Engine / Rule Model | ✅ 10 types |
| Development Environment | Rule IDE (`editor/`) | 🟡 Skeleton (382 lines) |
| Execution | Rule Runtime (`engine/`) | ✅ Stable |
| Adapter | File Rename (`scanner/`, `ui/`) | ✅ Stable |

## Current Version

**M9** — RuleInference Engine (Example → Rule)

## Completed Capabilities

- **Rule Inference** (M9): Pure-function engine, (original, desired) pairs → candidate RuleSteps via combinatorial search
- **Scanner**: Multi-path input, SMB-optimized (no `resolve()`)
- **Rule Engine**: 10 RuleStep types (replace, remove_text, regex_replace, case, trim, number, insert, date, add_prefix, add_suffix)
- **Rule Analysis**: Dependency pre-analysis (`uses_index` / `uses_metadata`)
- **Preview Engine**: Real-time preview with context (index, metadata)
- **RenamePlan Engine**: Conflict detection + legality checks
- **Rename Engine**: Policy-based execution (FAIL/SKIP/OVERWRITE)
- **Undo Engine**: Single-level undo via OperationLogger
- **Rule Presets** (M8): Save/load rule pipelines as named presets
- **Rule Manager**: Full CRUD + RuleStep editor
- **Rule Duplication** (M6): Clone existing rules
- **EditSession**: Working copy, dirty tracking, commit boundary, undo/redo
- **DomainValidator**: UI-independent rule/step validation
- **i18n**: zh_CN / en_US
- **Packaging**: PyInstaller build

## Development Roadmap

| Milestone | Capability | Status |
|---|---|---|
| M2–M8 | Batch Rename pipeline | ✅ |
| M9 | Example → Rule Inference | ✅ |
| M10 | Rule IDE | → Next |
| M11 | Rule Runtime hardening | Planned |
| Later | Additional adapters | Deferred
