# RuleForge — Milestone Exit Checklist

> **Status**: Active (M10.5-F)
> **Applies to**: All milestones

Every milestone must satisfy all criteria below before being marked
complete.  Items not applicable to a specific milestone should be
explicitly noted (e.g., "N/A — no public API changes").

## Architecture

- [ ] Boundaries preserved between layers (CLI / Workflow / Session / Runtime)
- [ ] Responsibilities remain clear and non-overlapping
- [ ] No component bypasses its designated entry point
- [ ] Presentation layers contain no business logic
- [ ] No duplicated execution paths

## Public API

- [ ] Public API compatibility preserved (no breaking changes without ADR)
- [ ] New public types/methods documented in `API_CONTRACT.md`
- [ ] Public/internal boundary respected (no new internal module exposure)
- [ ] Machine-readable output contracts remain stable

## Workflow & State

- [ ] `SessionState` transitions remain valid and enforced
- [ ] Failed operations do not advance state
- [ ] Commit requires successful validation
- [ ] Terminal states remain terminal (unless recovery workflow introduced)

## Testing

- [ ] Complete regression suite passes (known failures acknowledged)
- [ ] New functionality has corresponding tests
- [ ] Test coverage not weakened
- [ ] Public API contracts verified by tests
- [ ] CLI behavior verified by integration tests

## Documentation

- [ ] `AGENTS.md` updated (git baseline, behavior changes, architecture)
- [ ] ADRs recorded in `DECISION_LOG.md` for architectural decisions
- [ ] `ADR_INDEX.md` updated if new ADRs added
- [ ] `API_CONTRACT.md` updated if public API changed
- [ ] `ARCHITECTURE.md` updated if module structure changed
- [ ] `CONSTITUTION.md` reviewed for consistency with current architecture

## Compatibility

- [ ] No undocumented breaking changes
- [ ] Behavior consistent with documented contracts
- [ ] Migration path documented if backward compatibility affected

## Smoke Test

- [ ] Real-world usage validation performed
- [ ] Complete workflow verified (entry → exit)
- [ ] Error paths verified (non-zero exit codes, clear messages)

## Git

- [ ] Stable baseline tag created (`Mxx-complete`)
- [ ] All related files committed
- [ ] Commit messages describe scope and impact

## Sign-off

| Role | Date | Initials |
|---|---|---|
| Implementation | | |
| Testing | | |
| Documentation | | |
| Review | | |
