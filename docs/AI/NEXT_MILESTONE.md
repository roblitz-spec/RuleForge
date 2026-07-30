# RuleForge — Next Milestone Planning

## Product Direction

AI-assisted Rule IDE. Core value: Example → Rule Inference → Rule → Test/Preview → Execute → Reuse. ResourceHub is the origin; batch file rename is the initial adapter.

## Completed Milestones

| Milestone | Feature | Tests | Tag |
|---|---|---|---|
| M2–M8 | Batch Rename pipeline (scanner, rules, preview, rename, undo, presets) | 447 | M8-complete |
| M9 | RuleInference Engine (Example → Rule) | 480 | M9-complete |

## Strategic Roadmap

| Milestone | Capability | Rationale |
|---|---|---|
| M10 | **Rule IDE** — editing, inspection, testing/debugging, preview, persistence/reuse | Core development environment |
| M11 | **Rule Runtime** — reliable execution, batch processing, error handling, recovery | Production-grade execution |
| Later | Additional adapters/use cases | Post-core extensibility |

## M10 Candidate Scope

Build the Rule IDE on the existing `editor/` skeleton (EditSession, DomainValidator):

- Rule editing UI (step CRUD, parameter editing)
- Rule inspection (visualize step pipeline)
- Testing/debugging (apply rule to test inputs, preview results)
- RuleInference integration (paste examples → get candidate rules)
- Persistence (save/load beyond presets)

## Deferred

| Feature | Reason |
|---|---|
| Filter System (ex-P1) | Subsumed into Rule IDE inspection features |
| EXIF Date (ex-P2) | Adapter-level feature; defer to after M11 |
| Variables (ex-P4) | Requires RuleEngine extension; defer to M10+ |
| Prefix/Suffix Merge | Compatibility risk; needs migration plan |
