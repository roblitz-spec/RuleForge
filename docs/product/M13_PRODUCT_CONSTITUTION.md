# RuleForge — Product Constitution v1.0

_M13.0 — Product Baseline.  This document defines what RuleForge is and is not.
It does not specify implementation._

---

## 1. Product Vision

**RuleForge is a Local-First Personal Automation Workspace.**

It enables ordinary users to safely complete local file automation tasks
through four stages: **Plan → Preview → Execute → Rollback**.

Every design decision flows from eight commitments:

| Commitment | Meaning |
|---|---|
| **Local First** | All core capabilities work on the user's machine.  No server required. |
| **Offline First** | The product is fully functional without a network connection.  Network is an enhancement, never a requirement. |
| **Task First** | Users think in tasks ("rename these photos"), not in implementation details ("apply regex step 1 then case step 2"). |
| **Safe First** | Every destructive action has a preview and a rollback path.  Users should never fear clicking "Execute". |
| **Trust First** | Every automated action is understandable before execution.  Users see what will happen, why, and what risks exist. |
| **Human Override** | System proposes, user decides.  No automation component — rule engine, workflow, AI, or plugin — may bypass user confirmation. |
| **Progressive Disclosure** | Simple tasks are simple.  Advanced capabilities are available but never forced upon the user. |

---

## 2. Product Positioning

### What RuleForge Is NOT

| Misconception | Clarification |
|---|---|
| **Not an AI-first product** | AI is an optional provider.  The core product works without AI.  AI enhances, it does not define. |
| **Not a cloud automation platform** | RuleForge runs locally.  Cloud connectivity (remote storage, cloud AI) is optional and additive. |
| **Not a generic low-code platform** | RuleForge targets file automation specifically.  It does not compete with Zapier, n8n, or Node-RED. |
| **Not a programmer IDE** | RuleForge is not VS Code.  It does not require programming knowledge.  Power users can author rules, but rule authoring is a progressive path, not the entry point. |
| **Not just a batch rename utility** | File renaming is the initial application (ResourceHub).  The Workspace hosts multiple applications over time. |

### What RuleForge IS

| Identity | Description |
|---|---|
| **Personal Automation Workspace** | A single environment for planning, previewing, executing, and rolling back file transformations. |
| **Local productivity platform** | Runs on the user's machine.  Files stay local.  No upload required. |
| **Safe automation environment** | Preview before execute.  Rollback after execute.  No irreversible actions. |

---

## 3. Design Principles

### 3.1 Local First

- **Why**: Users should not need a server, an account, or an internet connection to automate their files.
- **What**: File discovery, planning, execution, and rollback all work locally.
- **Avoids**: Mandatory cloud sign-up, server-side processing, remote-only features.

### 3.2 Task First

- **Why**: Users arrive with a goal ("rename my vacation photos"), not with technical knowledge of rule engines.
- **What**: The product presents tasks and outcomes, not step types and regex patterns.  Technical concepts (rules, steps, plugins) are progressively disclosed.
- **Avoids**: Exposing implementation details as the primary interface.  Rule authoring is a power-user mode, not the default.

### 3.3 Safe First

- **Why**: File operations are destructive by nature.  Trust is earned through transparency and reversibility.
- **What**: Every execution is preceded by a preview.  Every execution can be rolled back.  Conflict detection warns before data loss.
- **Avoids**: Blind execution, irreversible operations, ambiguous outcomes.
- **Extended by**: [Trust First](#37-trust-first) (explainability) and [Human Override](#38-human-override) (final decision authority).

### 3.4 Progressive Disclosure

- **Why**: A product that shows everything at once overwhelms beginners and wastes screen space for experts.
- **What**: Simple tasks require minimal interaction.  Advanced capabilities (custom rules, plugins, workflows) are revealed as the user's needs grow.
- **Avoids**: Feature-dense screens, mandatory configuration wizards, forcing all users through the same complexity.

### 3.5 Workspace First

- **Why**: Individual tools (renamer, rule editor) are useful alone, but a unified workspace creates a coherent experience and enables cross-application workflows.
- **What**: The Workspace is the shell.  Applications (ResourceHub, Rule Studio, future apps) live inside it.  Tasks, history, and settings span applications.
- **Avoids**: Standalone disconnected tools, independent launch points, per-application silos.

### 3.6 AI Optional

- **Why**: AI is powerful but not universally available, trusted, or desired.  The product must not depend on it.
- **What**: Core functionality works without AI.  AI providers (local models, cloud models, none) are selectable and replaceable.
- **Avoids**: Hard-coding any AI provider, making AI a requirement for core flows, designing AI-only features.

### 3.7 Trust First

- **Why**: Automation without explanation erodes trust.  Users who understand what will happen and why are confident users.
- **What**: Before execution, the system answers four questions for the user: (1) What will the system do? (2) Why this result? (3) Which rule or step produced each change? (4) Are there conflicts or risks?  Complexity is hidden inside the system, but the automation outcome must be understandable.
- **Avoids**: Black-box automation, unexplained results, hiding rule provenance from the user.  The goal is **Plan → Preview → Explanation → User Decision → Execute** — not Plan → Execute.

### 3.8 Human Override

- **Why**: Automation is a tool, not an authority.  The user must always retain final control over their files.  This is a long-term product principle, independent of whether AI is present.
- **What**: The system proposes, the user decides.  No automation component — RuleEngine, WorkflowEngine, local intelligence, cloud AI, or plugins — may bypass the sequence: **Plan → Preview → User Confirmation → Execute → Rollback**.  Any intelligence capability (present or future) may only generate or suggest plans; it may never take final control of file modification.
- **Avoids**: Auto-execution without confirmation, AI-initiated file changes, plugins that bypass the preview/confirm flow, any path that removes the user from the decision loop.

---

## 4. Target Users

### Primary Users

| Persona | Needs |
|---|---|
| **Ordinary computer users** | Rename a folder of files.  Add dates to photos.  Clean up document names.  No technical knowledge assumed. |
| **Photographers** | Batch-rename RAW+JPEG pairs.  Apply date-based naming.  Organize shoots into folders. |
| **Office workers** | Standardize report filenames.  Add project codes.  Clean up exported files. |
| **Content creators** | Organize assets.  Apply consistent naming.  Prepare files for publishing. |

### Advanced Users

| Persona | Needs |
|---|---|
| **Power users** | Create reusable rules.  Chain multiple transformations.  Apply rules across directories. |
| **Rule authors** | Define custom transformation logic.  Share rules with others.  Compose rules from existing ones. |

**Progressive complexity, not separate products.**  A primary user starts with a simple task and may grow into rule authoring over time — within the same application.

---

## 5. Core User Journey

```
Open Workspace
      │
      ▼
Choose a task (e.g., "Rename files")
      │
      ▼
Generate a plan (RuleForge proposes what will happen)
      │
      ▼
Preview (see the result before it happens)
      │
      ▼
Confirm (approve or adjust)
      │
      ▼
Execute (RuleForge performs the transformation)
      │
      ▼
Review (see what actually happened)
      │
      ▼
Rollback if necessary (undo with one action)
```

**Users think in tasks, not implementation details.**  The product translates
"rename these photos with today's date" into the underlying rule steps
automatically.  Users who want to inspect or modify the underlying rules can
do so — but they never have to.

---

## 6. Workspace Model

RuleForge evolves from a single-purpose tool into a multi-application
workspace.

```
RuleForge Workspace
├── ResourceHub          File renaming and organization (current application)
├── Rule Studio          Rule authoring, testing, and sharing (future)
└── Future Applications  Additional automation domains (future)
```

### ResourceHub → Workspace Transition

ResourceHub (the current batch-rename application) becomes an application
**inside** the Workspace, rather than the product itself.  The Workspace
provides shared capabilities (task management, history, settings, plugin
management) that all applications inherit.

This is an architectural direction, not an immediate migration.  ResourceHub
continues to function as-is during the transition.

---

## 7. Information Architecture

High-level logical areas.  No UI layout is implied.

| Area | Purpose |
|---|---|
| **Workspace** | The shell.  Contains all applications, tasks, and global settings. |
| **Tasks** | User-initiated automation tasks.  Each task has a type, target, plan, and result. |
| **Applications** | Registered applications (ResourceHub, Rule Studio).  Each application provides task types. |
| **Preview** | Before-execution view of what will change.  Per-file diff.  Conflict warnings. |
| **History** | After-execution record of what changed.  Per-task results.  Rollback availability. |
| **Settings** | Global preferences, AI provider selection, plugin management. |

---

## 8. Offline-First Strategy

The following capabilities must always function without a network connection:

| Capability | Offline |
|---|---|
| File discovery (scanning directories) | ✅ |
| Planning (generating rename plans) | ✅ |
| Rule management (create, edit, save, load) | ✅ |
| Preview (showing planned changes) | ✅ |
| Execution (performing file operations) | ✅ |
| Rollback (undoing operations) | ✅ |
| History (viewing past operations) | ✅ |

**Network should only enhance the product.**  Examples of network-enhanced
capabilities: cloud AI providers for rule inference, remote file storage for
cross-device access, rule sharing with other users.

No core capability may require a network connection.  If a network-enhanced
feature is unavailable, the product degrades gracefully (e.g., "Cloud AI
unavailable — using local rules" or "Offline — sharing disabled").

---

## 9. Intelligence Strategy

### AI is an Optional Provider

| Aspect | Rule |
|---|---|
| **Core product** | Functions without AI.  All capabilities work with manual rule definition. |
| **AI as enhancement** | AI can assist with rule inference, suggestions, and automation — but is never required. |
| **Provider model** | AI is accessed through a provider abstraction.  Providers are selectable and replaceable. |

### Possible Future Providers

| Provider | Description |
|---|---|
| **None** | No AI.  Fully manual rule creation.  This must always be supported. |
| **Local models** | On-device inference via local LLMs.  No data leaves the machine. |
| **Cloud models** | Remote AI services.  Optional.  Requires network and user consent. |

**No provider-specific implementation in the core product.**  The provider
abstraction ensures that switching from "None" to "Local" to "Cloud" does
not require rewriting application logic.

**No AI workflow design in this constitution.**  The specific AI-assisted
user flows (inference UX, suggestion UI, confidence display) will be
designed in a future product specification.

---

## 10. Technical Relationship to M12

### M12 Architecture Remains Unchanged

- `ExecutionPipeline` remains the primary execution runtime.
- `RenamePlanEngine` remains the Planning SSOT.
- `RollbackPlugin` remains the unified rollback capability.
- `ExecutionIntegrationService` remains the Thin Integration Layer.
- All frozen modules remain frozen.

### M13 Builds Upon M12

M13 constructs the **user experience** on top of the existing M12 runtime:

| Layer | M12 (existing) | M13 (adds) |
|---|---|---|
| **Execution** | ExecutionPipeline, RenameExecutionEngine | (unchanged) |
| **Planning** | RenamePlanEngine (SSOT) | (unchanged) |
| **Integration** | ExecutionIntegrationService | (unchanged) |
| **Application** | MainWindow (Legacy GUI) | Workspace shell, application model |
| **User Experience** | Dialog-based | Workspace-based with progressive disclosure |

M13 is a **product evolution**, not an architecture refactoring.  The
runtime remains stable.  The user-facing layer is redesigned around the
product vision.

---

## 11. Product Roadmap

Direction only.  No dates.  No commitments.

```
M13.0  Product Constitution           ← this document
  │
  ▼
Workspace Shell                       Application framework, navigation
  │
  ▼
ResourceHub Integration               Current renamer as first application
  │
  ▼
Rule Studio                           Rule authoring, testing, sharing
  │
  ▼
Plugin Framework (UX)                 User-facing plugin management
  │
  ▼
Workflow Capability                   Multi-step task composition
  │
  ▼
Local Intelligence Provider           On-device AI for rule inference
  │
  ▼
Optional Cloud Intelligence           Remote AI providers
```

Each milestone builds on the previous.  The Workspace Shell establishes the
application model that ResourceHub, Rule Studio, and future applications
inhabit.

---

## 12. Product Non-Goals

What RuleForge **intentionally avoids**:

| Non-Goal | Rationale |
|---|---|
| **Feature accumulation** | More features ≠ better product.  Each addition must earn its place against the design principles. |
| **Complexity for its own sake** | Advanced capabilities exist for power users but must not complicate the primary user's experience. |
| **Mandatory cloud dependency** | Violates Local First and Offline First. |
| **Mandatory AI dependency** | Violates AI Optional. |
| **Breaking offline capability** | Every release must preserve full offline functionality for core capabilities. |
| **Becoming a generic automation platform** | Focus on file automation.  Resist scope creep into unrelated domains. |
| **Becoming a programmer tool** | Power users and rule authors are welcome, but the product is designed for ordinary users first. |

---

## 13. Workspace Experience Design

_M13.1-A — UX baseline.  Describes interaction models and user flow.
No pixel-level UI mockups.  No implementation details._

### 13.1 Workspace Goals

The Workspace is the user's primary working environment.

| The Workspace is | The Workspace is NOT |
|---|---|
| A place to work on tasks | A launcher for individual tools |
| A coherent environment with shared history and settings | A dashboard of disconnected widgets |
| Task-centered, not tool-centered | A traditional IDE with panels and tabs everywhere |

Users open the Workspace to accomplish a goal ("rename my photos").
They think in tasks, not in applications.  The Workspace helps them
choose, configure, preview, and complete that task — without needing
to know which application handles it.

---

### 13.2 Workspace Layout

Logical regions only.  No layout engine or pixel positions are implied.

| Region | Purpose |
|---|---|
| **Navigation** | Access to applications, tasks, and settings.  Minimal and persistent. |
| **Current Task** | The active task: what is being done, what step the user is on. |
| **Preview** | Before-execution view of planned changes.  Per-file diff with explanations. |
| **Activity / History** | After-execution record.  Past tasks, results, rollback availability. |
| **Applications** | Registered applications available for task creation. |
| **Settings** | Global preferences, AI provider selection, plugin management. |

The layout adapts to the task.  A user renaming files sees different
regions than a user authoring a rule — but the Workspace shell
(Navigation, Activity, Settings) stays consistent.

---

### 13.3 Home Experience

A first-time user opening RuleForge should be greeted with:

> **"What would you like to do today?"**

Suggested starting points:

| Task | Description |
|---|---|
| **Rename files** | Clean up a folder of files with consistent naming |
| **Organize photos** | Apply date-based naming to photo collections |
| **Organize downloads** | Standardize downloaded file names |
| **Continue previous work** | Reopen a recent task or rule set |

Advanced concepts (rule authoring, plugins, workflows, AI providers)
are not exposed on first launch.  The home experience is task-oriented,
not feature-oriented.

---

### 13.4 Application Model

Applications live inside the Workspace.  They share one runtime and
one user session.

| Application | Status | Description |
|---|---|---|
| **ResourceHub** | Initial | File renaming and organization.  The first application available in the Workspace. |
| **Rule Studio** | Future | Rule authoring, testing, and sharing. |
| **Workflow** | Future | Multi-step task composition across applications. |
| **History** | Future | Comprehensive task and execution history browser. |

Applications are not standalone executables.  They are capabilities
registered with the Workspace that provide task types, views, and
configuration.  The Workspace provides the shell: navigation, task
management, settings, and cross-application history.

---

### 13.5 Task-First Interaction

The preferred workflow for every task:

```
Choose a task           "What do you want to do?"
      │
      ▼
Configure the task      Select target files, choose options
      │
      ▼
Generate a plan         RuleForge proposes what will change
      │
      ▼
Preview                 See each change before it happens
      │
      ▼
Explain (if needed)     Understand why each change was proposed
      │
      ▼
User confirmation       Approve or adjust
      │
      ▼
Execute                 RuleForge performs the transformation
      │
      ▼
Review                  See what actually happened
      │
      ▼
Rollback (if needed)    Undo with one action
```

**Users think in goals, not implementation.**  "Rename these photos
with today's date" is a task.  "Add date step with format %Y-%m-%d
at position prefix" is an implementation detail.  The product handles
the translation.

---

### 13.6 Progressive Disclosure

Three experience levels within a single product:

| Level | User | Sees |
|---|---|---|
| **Level 1** | Ordinary user | Task selection, file picker, preview, execute, rollback.  Essential controls only. |
| **Level 2** | Power user | Rule browser, rule customization, advanced options, task history. |
| **Level 3** | Professional user | Rule authoring, diagnostics, execution traces, plugin management, workflow capabilities. |

Users grow naturally.  A Level 1 user who wonders "why did it add that
prefix?" can expand the explanation and discover the underlying rule.
A Level 2 user who wants to create reusable rules can open Rule Studio
from the same Workspace.  No mode switch required — capabilities
appear as the user reaches for them.

---

### 13.7 Trust Experience

Expands the [Trust First](#37-trust-first) principle into interaction design.

Before execution, the UI communicates:

| Question | How the UI Answers |
|---|---|
| **What will happen?** | Per-file preview showing old name → new name.  Count of files affected. |
| **Why?** | Explanation linked to the specific rule or step that produced each change.  "This file was renamed because the 'Add Date' rule applied." |
| **Which rule applies?** | Rule provenance per change.  Users can click through to see the rule definition if they choose. |
| **Are there conflicts?** | Warnings for name collisions, case-only renames on Windows, files that would be overwritten. |

**Internal runtime terminology is not exposed.**  Users see "Add date"
not "DateRuleStep(format='%Y-%m-%d', position='prefix')".  The
explanation is in the user's language, not the engine's.

---

### 13.8 Human Control

Expands the [Human Override](#38-human-override) principle into
interaction design.

| Behavior | Rule |
|---|---|
| **Execution always follows confirmation** | No task executes without explicit user approval.  The Execute button is only active after preview is shown and understood. |
| **Rollback is always visible** | After execution, rollback is one action away.  The user never wonders "can I undo this?" |
| **Automation proposes, never decides** | AI-suggested rules, workflow-generated plans, and plugin-produced results are presented as proposals — never auto-applied. |
| **No hidden execution paths** | Every file modification is traceable to a user-initiated task.  No background automation, no silent changes. |

These behaviors apply regardless of whether the intelligence behind
a proposal is a rule engine, a workflow, a local model, or a cloud AI.

---

### 13.9 Workspace Principles

Practical UX principles for workspace design:

| Principle | Meaning |
|---|---|
| **Calm interface** | The Workspace shows what is needed for the current task.  Nothing more. |
| **Minimal cognitive load** | Each screen answers one question for the user.  The user never has to hold multiple contexts in mind. |
| **Progressive complexity** | Advanced features exist but never intrude on simple tasks. |
| **Consistent terminology** | The same concept has the same name everywhere.  "Preview" means the same thing in ResourceHub and Rule Studio. |
| **Explain before execute** | The user always sees what will happen and why before committing. |
| **Undo whenever practical** | If an action can be reversed, a visible undo path exists. |

---

### 13.10 Success Criteria

Qualitative outcomes, not measurable metrics:

A new user should:
- Understand the Workspace's purpose within the first minute of use
- Complete a basic task (select files → preview → rename) without reading documentation
- Feel confident before clicking Execute
- Know how to recover if the result is not what they expected

A returning user should:
- Find their previous tasks and rules easily
- Progress from task execution to rule customization at their own pace
- Discover advanced capabilities (plugins, workflows, AI) without being pushed toward them

---

*M13.1-A Workspace Experience Design baseline.  This section defines the
user experience direction.  Specific UI design, layout implementation, and
visual design are deferred to future product specifications.*

---

## 14. Workspace Architecture Impact Review

_M13.1-B — Architecture review.  Evaluates whether the M13.1-A Workspace
experience design can be implemented while preserving the M12 Architecture
Baseline.  No implementation proposals.  No architecture redesign._

### 14.1 Runtime Compatibility

| Component | Impact | Rationale |
|---|---|---|
| **RenamePlanEngine** | **No impact** | Planning SSOT remains unchanged.  The Workspace consumes `RenamePlan` the same way the current GUI does — via `RenamePlanEngine.generate()`.  Task-first interaction renames the user-facing language ("generate a plan") without touching the underlying API. |
| **ExecutionIntegrationService** | **Minor UI-facing impact** | The Integration Layer is a Thin Adapter (A/B/C class).  A Workspace-based UI would call `execute(plan, rule)` through the same contract.  The `ExecutionContext` construction, `ExecutionPipeline` invocation, and `ExecutionResult` mapping remain identical.  Only the caller changes (`MainWindow` → Workspace shell). |
| **ExecutionPipeline** | **No impact** | Primary runtime is frozen (M11).  The Workspace does not modify pipeline behavior, engine selection, or result structure.  `ExecutionPipeline.run(ctx, engine)` is called identically regardless of UI framework. |
| **Rollback** | **No impact** | `RollbackPlugin` is frozen (M12-D).  The Workspace exposes rollback as a user-facing action ("Undo") through the same `rollback()` API.  No plugin modification required. |
| **ExecutionTrace** | **No impact** | Trace and metrics are engine outputs.  The Workspace may display them differently (e.g., in a History application), but the trace data model is unchanged. |

**Conclusion**: All M12 runtime components are compatible with the Workspace
model.  The Integration Layer is the only component that touches UI, and its
contract is designed for exactly this kind of caller substitution.

---

### 14.2 UI Layer Impact

The Workspace introduces new UI concepts without replacing the runtime.
These are conceptual descriptions only — no class names, no implementation.

| Concept | Description | Relationship to M12 |
|---|---|---|
| **Workspace Shell** | Top-level container providing navigation, task management, and cross-application consistency.  Replaces the current single-window `MainWindow` as the user-facing entry point. | New UI layer above existing runtime.  `MainWindow` becomes an application view inside the shell. |
| **Application Container** | Hosts individual applications (ResourceHub, Rule Studio).  Each application provides task types and views.  Applications share the runtime via `ExecutionIntegrationService`. | Applications are UI constructs.  They delegate to the existing runtime — they do not replace it. |
| **Navigation Model** | Task-centered navigation: "what do you want to do?" → configure → preview → execute.  Not tool-centered (file menu → rename dialog). | Navigation is pure UI.  The underlying flow (plan → preview → execute → rollback) is already implemented and unchanged. |

**These concepts are additive.**  They wrap the existing runtime in a new
user experience without modifying execution, planning, or rollback.

---

### 14.3 Application Model Compatibility

**ResourceHub can operate as an application inside the Workspace without
changing its execution responsibilities.**

| Concern | Analysis |
|---|---|
| **Execution path** | ResourceHub's execution path (`MainWindow._on_rename()` → `ExecutionWorker` → `ExecutionIntegrationService` → `ExecutionPipeline`) is self-contained.  Wrapping it in an Application Container does not alter this path. |
| **Planning path** | `RenamePlanEngine.generate()` is called with the same inputs regardless of whether the caller is `MainWindow` or a Workspace application view. |
| **State isolation** | ResourceHub's current state (selected files, active rule, preview results) lives in `MainWindow`.  Moving this state into an Application Container is a UI refactoring, not a runtime change. |
| **Rollback** | `RollbackPlugin` is global (one instance).  The Workspace would expose rollback through a shared Activity/History view rather than per-application undo — but the underlying `rollback()` API is unchanged. |

**No runtime refactoring is required for ResourceHub to become a Workspace application.**

---

### 14.4 Extension Readiness

The M12 architecture naturally supports future applications through its
existing layering.

| Future Application | Architecture Readiness |
|---|---|
| **Rule Studio** | The RuleEngine, RenamePlanEngine, and PreviewEngine are already pure-functional and UI-agnostic.  A Rule Studio application would consume these same engines through the same `RuleWorkflow` API.  No engine modifications needed. |
| **History** | `OperationLogger` already maintains cross-run history.  `ExecutionTrace` provides per-run detail.  A History application would query these existing data sources through their current APIs. |
| **Workflow** | `WorkflowPlugin` (M12-G) already provides step orchestration.  A Workflow application would provide a user-facing editor that produces `Workflow` definitions consumed by the existing plugin. |

**The architecture was designed for this.**  The Plugin Framework (M12-B)
was built on the principle that new capabilities enter through plugins —
applications are the user-facing equivalent of that principle.

---

### 14.5 Risks

| Risk | Severity | Mitigation Principle |
|---|---|---|
| **UI coupling to runtime internals** | Medium | The Workspace shell must call only public APIs (`ExecutionIntegrationService.execute()`, `RenamePlanEngine.generate()`).  Direct calls to `ExecutionPipeline.run()`, `EngineRegistry.create()`, or internal engine methods would break the Integration Layer contract.  Mitigation: enforce the Runtime Contract compliance checklist (Section 10). |
| **State management complexity** | Medium | Currently, `MainWindow` owns all UI state (selection, preview, results).  Distributing state across a shell + multiple applications risks inconsistency.  Mitigation: the Workspace shell owns task lifecycle state; applications own domain-specific state.  Clear ownership boundaries prevent duplication. |
| **Navigation complexity** | Low | Task-centered navigation ("what do you want to do?") is simpler than tool-centered navigation (menus, toolbars, dialogs).  The risk is over-engineering the navigation model before applications exist.  Mitigation: start with a single application (ResourceHub) and add navigation patterns as new applications justify them. |
| **Application isolation leakage** | Low | Applications share a runtime but must not share mutable state inadvertently.  Mitigation: each application receives its own `ExecutionIntegrationService` instance (thin, stateless beyond `RollbackPlugin` reference).  Shared concerns (rollback, history) go through well-defined APIs. |

---

### 14.6 Compatibility Summary

| Question | Answer |
|---|---|
| **M12 Runtime remains valid?** | **Yes.** All frozen components (RenamePlanEngine, ExecutionPipeline, ExecutionIntegrationService, RollbackPlugin, ExecutionTrace) are compatible.  The Workspace is a UI layer addition — it does not modify, replace, or bypass any M12 runtime component. |
| **Product Constitution remains internally consistent?** | **Yes.** The Workspace Experience Design (Section 13) extends the M13.0 principles (Section 3) into UX direction without contradicting any principle.  Trust First and Human Override are reinforced, not weakened, by the Workspace model. |
| **Workspace can evolve incrementally?** | **Yes.** The architecture supports starting with a single application (ResourceHub) inside a Workspace shell and adding applications (Rule Studio, History, Workflow) over time.  Each addition consumes existing APIs without requiring runtime changes. |

---

*M13.1-B Architecture Impact Review.  The M13.1-A Workspace design is
compatible with the M12 Architecture Baseline.  No runtime modifications
are required.  Implementation can proceed incrementally, starting with
the Workspace Shell + ResourceHub as the first application.*

---

## 15. Workspace Shell Implementation Planning

_M13.1-C — Implementation strategy.  Defines a safe, incremental path
from the current ResourceHub UI to the first-generation RuleForge Workspace.
No implementation tasks.  No architecture redesign._

### 15.1 Planning Objective

The Workspace Shell is:

| Characteristic | Description |
|---|---|
| **A product-layer evolution** | The runtime (M12) does not change.  Only the user-facing layer evolves. |
| **An incremental UI transition** | ResourceHub continues to function during every stage.  No "big bang" rewrite. |
| **Not an architectural rewrite** | RenamePlanEngine, ExecutionPipeline, RollbackPlugin, and all frozen modules remain untouched. |
| **Not a runtime redesign** | ExecutionIntegrationService retains its Thin Integration Layer contract.  No new execution paths. |

**The objective is to wrap existing capabilities inside a Workspace
experience.**  The same engines, the same pipeline, the same rollback —
presented through a task-centered, progressively-disclosed interface.

---

### 15.2 Implementation Principles

| # | Principle | Meaning |
|---|---|---|
| 1 | **Preserve M12 runtime unchanged** | No modification to any frozen module.  The Integration Layer contract is the boundary. |
| 2 | **Incremental delivery** | Each stage produces a working, shippable state.  No long-running feature branches. |
| 3 | **Small reviewable changes** | Each change is small enough to review in one sitting.  Refactoring and feature work are never combined in the same change. |
| 4 | **Reversible implementation steps** | Every stage can be rolled back without data loss or broken state.  Feature flags or conditional branching enable this. |
| 5 | **Existing functionality remains available** | At no point during the transition is ResourceHub's current functionality degraded or unavailable.  Users can always rename files. |

---

### 15.3 Scope Definition

#### In Scope

| Item | Description |
|---|---|
| **Workspace container** | Top-level window or shell that hosts applications.  Replaces the current single-window `MainWindow` as the entry point. |
| **Navigation structure** | Task-centered navigation: "what do you want to do?" as the primary interaction pattern. |
| **ResourceHub integration** | ResourceHub operates as the first application inside the Workspace.  All existing rename functionality preserved. |
| **Task-oriented entry flow** | Users enter through task selection rather than file menus and toolbars. |

#### Out of Scope

| Item | Rationale |
|---|---|
| **Rule Studio implementation** | Future application.  Requires its own M13 milestone. |
| **Plugin framework UI** | Plugin management UI is a separate concern from the Workspace Shell. |
| **Workflow editor** | Future application.  Depends on Rule Studio. |
| **AI integration** | AI provider selection and inference UI are future milestones. |
| **Runtime refactoring** | M12 is frozen.  No runtime changes — by design. |

---

### 15.4 Incremental Delivery Stages

Goals only.  No schedules.  No task assignments.

#### Stage 1 — Workspace Shell Appears

**Goal**: The Workspace container exists and ResourceHub runs inside it.

- A new top-level window or shell hosts the application area.
- ResourceHub's current `MainWindow` content is embedded as the first application view.
- No navigation changes yet.  No task-first entry.  ResourceHub looks and works the same — it just lives inside a shell.
- **Success**: Users see a Workspace window.  ResourceHub functions identically to before.

#### Stage 2 — Navigation and Application Container Mature

**Goal**: The shell provides navigation and the application model becomes visible.

- Navigation sidebar or equivalent appears, showing available applications (initially: ResourceHub).
- Application container provides consistent chrome (title, close, minimize) for each application.
- Switching between applications (when more are added) is possible through navigation.
- **Success**: Users navigate via the shell.  The concept of "applications inside a workspace" is visible.

#### Stage 3 — Task-First Entry Replaces Tool-First Entry

**Goal**: Users enter through tasks, not tools.

- Home screen presents "What would you like to do today?" with task suggestions.
- Selecting "Rename files" opens ResourceHub pre-configured for that task.
- The underlying `MainWindow` tool interface is still available for power users but no longer the default entry point.
- **Success**: A new user can complete a rename task without seeing file menus or toolbars.

#### Stage 4 — Advanced Capabilities Become Progressively Discoverable

**Goal**: Power-user features are present but not intrusive.

- Rule browser becomes accessible from within ResourceHub (Level 2 disclosure).
- Execution traces and diagnostics become accessible from History/Activity (Level 3 disclosure).
- The Workspace shell adapts to show more capabilities as the user demonstrates interest.
- **Success**: A Level 1 user sees only task essentials.  A Level 3 user can access traces, rules, and diagnostics without leaving the Workspace.

---

### 15.5 Architectural Boundaries

Implementation must not alter any of the following:

| Component | Boundary |
|---|---|
| **RenamePlanEngine** | Planning SSOT.  Called through existing public API only. |
| **ExecutionIntegrationService** | Thin Integration Layer.  Responsibilities defined by Runtime Contract (Section 10).  No new methods, no business logic. |
| **ExecutionPipeline** | Primary runtime.  Called through `ExecutionIntegrationService.execute()`.  No direct invocation. |
| **Rollback** | Unified rollback via `RollbackPlugin`.  No alternative undo path. |
| **ExecutionTrace** | Engine output.  Displayed, not modified. |

**Only the presentation layer evolves.**  The UI may be reorganized,
renamed, and restructured — but every UI action must delegate to the
existing runtime through the existing Integration Layer contract.

---

### 15.6 Review Gates

Before progressing from one stage to the next, confirm:

| Gate | Check |
|---|---|
| **Product Constitution compliance** | Does the current state align with all 8 design principles? |
| **M12 compatibility** | Are all frozen modules untouched?  Is the Runtime Contract satisfied? |
| **Offline-first preserved** | Do all core capabilities work without a network connection? |
| **Trust First preserved** | Does the UI explain what will happen before execution? |
| **Human Override preserved** | Does execution always require explicit user confirmation? |
| **Existing functionality not regressed** | Can users still rename files, preview changes, and roll back?  Do all existing tests pass? |

Each gate is pass/fail.  A failed gate blocks progression.  The stage
must be corrected until all gates pass.

---

### 15.7 Completion Criteria

The first Workspace Shell is complete when:

- Users enter RuleForge through the Workspace, not through a bare `MainWindow`.
- ResourceHub operates as an application inside the Workspace, with all existing rename functionality preserved.
- The home experience answers "What would you like to do today?" with task-oriented suggestions.
- Existing workflows (scan → select rule → preview → rename → undo) continue to function.
- No runtime behavior changes have been introduced.
- All existing tests pass without modification.
- The M12 Architecture Baseline remains intact (frozen module audit: 11/11 CLEAN).

---

*M13.1-C Workspace Shell Implementation Planning.  Defines a 4-stage
incremental delivery path with architectural boundaries and review gates.
Implementation begins when M13 product baseline is approved.*

### Implementation Status

Workspace Shell maturity: **Completed**.  The shell is implemented and
functioning as the primary application shell — `WorkspaceWindow` wraps
`MainWindow` via `QStackedWidget`, sidebar navigation is present, and
the entry point (`main.py`) launches `WorkspaceWindow`.

Runtime isolation: **Verified**.  The Workspace implementation does not
introduce modifications to the M11/M12 runtime pipeline.  All frozen
modules (`ExecutionPipeline`, `RenameExecutionEngine`, `EngineRegistry`,
`ExecutionTrace`, `ExecutionMetrics`, `RenamePlanEngine`, `RollbackPlugin`,
`PluginFramework`, `ExecutionIntegrationService`, `OperationLogger`,
`ExecutionContext`) remain unchanged from the M12 baseline.

| Stage | Description | Status |
|---|---|---|
| Stage 1 | Workspace Shell — `WorkspaceWindow` wraps `MainWindow` via `QStackedWidget`; sidebar with navigation placeholders | ✅ Implemented |
| Stage 2 | Navigation — `_NavItem` custom widget; application switching via `_activate_app()`; workspace context header | ✅ Implemented |
| Stage 3 | Task-First Entry — `WorkspaceHome` landing page with 4 task cards; task → ResourceHub mapping; Home button | ✅ Implemented |
| Stage 4 | Context & Session — in-memory session tracking; recent activity section; "Continue Previous Work" reflects last task; safety reminders | ✅ Implemented |

**Files**: `ui/workspace_window.py` (WorkspaceWindow, WorkspaceApp, AppStatus, _NavItem, _APP_REGISTRY), `ui/workspace_home.py` (WorkspaceHome + _TaskCard), `main.py` (entry point).

### M13.3 Status

Workspace Application Framework maturity: **Foundation**.  The current
implementation provides a static application model:

- centralized application registry (`_APP_REGISTRY`)
- shared Workspace shell (`QStackedWidget`)
- application switching (`_activate_app`)
- reusable application structure (`WorkspaceApp` consumed by `_NavItem`)

The following are **not yet implemented**:
- plugin architecture
- dynamic discovery
- application lifecycle management
- extension points

| Stage | Description | Status |
|---|---|---|
| Stage 1 | Application Framework — `WorkspaceApp` frozen dataclass; `AppStatus`; `_APP_REGISTRY` static registration; `_NavItem` consumes `WorkspaceApp` | ✅ Implemented |
| Stage 2 | History — basic implementation: shares `OperationLogger`; table view with Refresh/Export/Clear | ✅ Implemented |
| Stage 3 | Rule Studio — foundation: integrates existing Rule Manager into Workspace; planned features displayed as placeholders | ✅ Implemented |
| Stage 4 | Workflow — foundation: establishes Workspace surface and future integration point; no execution capabilities | ✅ Implemented |

### Application Maturity Summary

| Application | Maturity | Capabilities |
|---|---|---|
| ResourceHub | Complete | Full rename workflow (scan, rule config, preview, execute, rollback) |
| History | Basic | Execution log table; Refresh, Export (CSV/TXT), Clear; shares `OperationLogger` |
| Rule Studio | Foundation | Rule Manager access via delegation; planned features (testing, validation, sharing, AI authoring) shown as placeholders |
| Workflow | Foundation | Product surface only; references ResourceHub for current single-task workflow; planned capabilities (multi-step, scheduling, templates, reports) shown as placeholders |

Files: `ui/workspace_window.py`, `ui/history_app.py`, `ui/rule_studio_app.py`, `ui/workflow_app.py`, `ui/workspace_home.py`, `main.py`.

### M13.4 — Working Workspace

Work Workspace maturity: **Product Experience**.  Builds on the Workspace
shell and application framework with session continuity features.

**Phase 1 — Session Persistence Foundation**

Established lightweight Workspace state persistence via QSettings:

- `workspace/last_app` — last active application ID
- `workspace/last_task` — last task title
- `workspace/recent_tasks` — up to 5 recent task titles (JSON)
- `closeEvent()` saves state on shutdown; `_on_task_selected()` persists immediately

Implementation: `config/settings.py` (3 new keys + 6 methods).

**Phase 2 — Working Workspace Experience**

- **Continue Last Session** — on startup, restores the last active
  Workspace application instead of always defaulting to home.
- **Actionable Recent Tasks** — home page renders recent tasks as
  clickable buttons; each navigates to ResourceHub with task context.
- **Navigation Restoration** — last active app highlighted in sidebar,
  context header and status bar reflect the restored state.
- **Immediate Persistence** — task selection writes to QSettings
  immediately (not just on close), surviving crashes.

Implementation: `ui/workspace_window.py` (`_restore_session` returns
`last_app_id`, `_activate_app` restores context), `ui/workspace_home.py`
(`set_recent` renders `QPushButton` widgets).

**Files**: `ui/workspace_window.py`, `ui/workspace_home.py`, `config/settings.py`.

### Runtime Boundary Summary

All 11 Runtime files unchanged from M12 baseline:
`ExecutionPipeline`, `RenameExecutionEngine`, `ExecutionContext`,
`EngineRegistry`, `ExecutionTrace`, `ExecutionMetrics`,
`RenamePlanEngine`, `RollbackPlugin`, `PluginFramework`,
`ExecutionIntegrationService`, `OperationLogger`.

Workspace state (QSettings) and Runtime state (in-memory) remain
isolated — no serialization of execution state, no pipeline
persistence, no background job restoration.

---

*M13.0 Product Baseline.  This constitution governs all M13+ product decisions.
It does not specify implementation, UI, or schedules.*
