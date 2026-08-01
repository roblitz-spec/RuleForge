# RuleForge — Project Identity

*Canonical project context.  Read this first.  Stable — changes only when
project identity changes.*

## 1. Project Overview

**RuleForge is an AI-assisted Rule IDE.**  It lets users define, test,
preview, and execute transformation rules.  File renaming is the initial
adapter — the platform supports pluggable execution engines for any
transformation domain.

| Field | Value |
|---|---|
| Target users | Developers, power users who need batch transformations |
| Core value | Example → Rule → Preview → Execute, with repeatable, auditable results |
| License | Apache 2.0 |

## 2. Current Status

| Field | Value |
|---|---|
| Current Milestone | M12 (closed) |
| Project Status | **Maintenance Mode** |
| Architecture Status | **Baseline Frozen** |
| Development Policy | **Maintenance First** |
| Primary Branch | `m11-execution-platform` |

See [README.md](README.md) for usage and quick start.
See [CHANGELOG.md](CHANGELOG.md) for milestone history.

## 3. Project Principles

These principles govern every architecture and code decision.
See [`docs/architecture/principles.md`](docs/architecture/principles.md) for
the full definitions and anti-patterns.

1. **Single Responsibility** — each module owns one concern
2. **Plugin First** — new capabilities enter through plugins, never by modifying engine or framework
3. **Composition First** — compose existing plugins before creating new ones
4. **Frozen Contract** — once frozen, public APIs never change
5. **Backward Compatibility** — all existing behaviour and tests must continue to pass
6. **Zero Cross-Plugin Dependency** — plugins import only from the Plugin Framework and stdlib
7. **Stable Public Contract** — every API designed for long-term stability
8. **Capability Decoupling** — plugins are independent, composable, replaceable

Also:

- **Single Source of Truth** — one concept, one authoritative definition
- **Documentation as Architecture** — document why, not just what

## 4. Architecture Snapshot

```
RuleEngine ── transforms filenames (pure functions)

     ↓

Execution Platform (M11) ── executes transformations
  5 engines: StringTransform, Rename, DryRun, Inspection, Batch

     ↓

Plugin Framework (M12-B) ── manages plugin registration, lifecycle, discovery
  Plugin ABC  ·  Registry  ·  Lifecycle State Machine

     ↓

Capability Plugins (M12-C…K) ── cross-cutting execution concerns
  Rollback  ·  Scheduler  ·  RemoteProvider  ·  Workflow
  Event  ·  Policy  ·  Validation  ·  Notification

     ↓

Composition ── capabilities compose at the caller level
  Audit = Event + Notification   ·   Rate-limit = Policy + Scheduler
```

For the full architecture: [`docs/architecture/overview.md`](docs/architecture/overview.md).
For the execution lifecycle: [`docs/architecture/execution-lifecycle.md`](docs/architecture/execution-lifecycle.md).

## 5. Canonical Documentation

| Document | Purpose |
|---|---|
| [README.md](README.md) | Project entry point — what, status, quick start |
| [docs/architecture/overview.md](docs/architecture/overview.md) | Architecture — layers, design principles |
| [docs/architecture/principles.md](docs/architecture/principles.md) | 8 binding architecture principles |
| [docs/architecture/adr/README.md](docs/architecture/adr/README.md) | Architecture Decision Records — why decisions were made |
| [docs/architecture/capability-handbook.md](docs/architecture/capability-handbook.md) | Capability API reference — all 8 plugins |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contributor guide — decision tree, template, rules |
| [CHANGELOG.md](CHANGELOG.md) | Milestone history (M2–M12) |
| [docs/governance/](docs/governance/) | Governance history (not normative) |
| [docs/ideas/ideas.md](docs/ideas/ideas.md) | Deferred capability candidates |

## 6. Maintenance Policy

| Allowed | Not Allowed |
|---|---|
| Bug fixes | New capability plugins |
| Documentation improvements | Framework refactoring |
| CI / tooling maintenance | Engine refactoring |
| Dependency maintenance | Contract-breaking changes |

Work exceeding these bounds requires a new Major Milestone (M13+),
planned and approved through formal governance.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the Capability Acceptance Rules.

## 7. AI Collaboration

### OpenHands (implementation agent)

Responsible for: implementation, bug fixes, testing, documentation
maintenance, repository housekeeping.

Operates within frozen contracts.  Does not design new architecture
or create new milestones without explicit approval.

Context file: [`AGENTS.md`](AGENTS.md).

### AI Reviewer (e.g. ChatGPT / Claude)

Responsible for: architecture discussion, technical review, design
analysis, risk assessment, milestone planning.

Does not modify code or repository state.

## 8. Restart Guide

If returning after months away, read in this order:

1. **PROJECT_IDENTITY.md** ← you are here
2. [README.md](README.md) — project status and quick start
3. [docs/architecture/overview.md](docs/architecture/overview.md) — architecture
4. [docs/architecture/adr/README.md](docs/architecture/adr/README.md) — key decisions
5. [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute

Do NOT start with historical milestone documents — the architecture
baseline supersedes them.

## 9. Project Timeline

```
M11 ── Execution Platform v1 ── M11-complete
  │
  ├── M12-A ── Batch Execution
  ├── M12-B ── Plugin Framework
  ├── M12-C…K ── 9 Capability Plugins
  │
M12 ── Capability Plugin Platform ── M12-K-complete
  │
  ├── Architecture Baseline Documentation
  ├── Documentation Audit & Cleanup
  │
  ▼
Maintenance Mode — Architecture Baseline Frozen
```

Full milestone details: [`CHANGELOG.md`](CHANGELOG.md).

---

*This is the canonical project context.  Modify only when project
identity, status, or principles materially change.*
