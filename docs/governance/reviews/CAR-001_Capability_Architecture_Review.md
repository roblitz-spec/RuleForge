# Capability Architecture Review — CAR-001

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-REV-015` | `REV` | `accepted` | `1.0` | `2026-07-29` |

| part_of |
|---|
| PAC-2 Architecture |

---

**Date**: 2026-07-29 | **Type**: Capability Architecture Review | **Scope**: PG-01 and PG-05 Capability Boundary Analysis

---

## Phase 1 — Governance Objectives

### O1: Governance Identity

| Dimension | Analysis |
|---|---|
| **Problem** | ResourceHub has no formal definition of its relationship to "Rule IDE." The project charter says ResourceHub "will evolve into Rule IDE," but this is a one-line assertion, not a governance position. PG-01 exists because stakeholders cannot agree on what the project IS. |
| **Expected outcome** | A governance position that answers: Is Rule IDE a rename, a subsystem, a milestone category, or a separate product? This position affects architecture, naming, roadmap, and external communication. |
| **Long-term stability** | Once decided, this position is stable for years. It changes only if the project fundamentally pivots. |
| **Future extensibility** | Low — one decision resolves it. The governance framework must handle the decision, not establish a recurring identity management process. |

**Verdict**: Governance Identity is required but is a **decision**, not a **capability**. It produces one artifact, not an ongoing governance process.

### O2: Versioning

| Dimension | Analysis |
|---|---|
| **Problem** | The repository has 12+ git tags, 4 different milestone labels, semantic versions on governance documents, and no definition of what any of them mean. `v0.1` appears in the window title; `v1.0` appears on governance documents; M-numbers appear everywhere. Nothing maps to anything. |
| **Expected outcome** | A versioning policy that defines: M↔v mapping, v1.0 criteria, when versions increment, what versioning scheme applies to what artifact type. |
| **Long-term stability** | Versioning policy is foundational — it must exist before any cross-document validation can occur. It changes rarely (once per major release). |
| **Future extensibility** | Medium — new artifact types may require versioning schema extensions. |

**Verdict**: Versioning is required as a **foundational capability**. It is the single most important unresolved PG item.

### O3: Traceability

| Domain | Analysis |
|---|---|
| **Problem** | Documents reference each other through content, filenames, and registry entries. There is no standard for how a document declares its dependencies or how consumers verify those dependencies are current. |
| **Expected outcome** | GS-05 (Traceability Standard) operationalized — all documents declare relationships in metadata; staleness is detectable. |
| **Long-term stability** | Stable once defined; relationship types change rarely. |
| **Future extensibility** | Low — 5 relationship types cover expected needs. |

**Verdict**: Traceability is required. GS-05 was accepted as a standard; the remaining work is operational adoption.

### O4: Governance Standards

| Domain | Analysis |
|---|---|
| **Problem** | Before PAC-2 Standards, governance work had no standard lifecycle, format, review process, naming convention, or traceability model. Each PG item reinvented its own process. |
| **Expected outcome** | GS-01 through GS-05 govern all future governance work. |
| **Long-term stability** | Standards are stable; amendments follow the 7-WP lifecycle. |
| **Future extensibility** | Extensible — new standards follow the same GOV-ID and GUIDE type pattern. |

**Verdict**: Already delivered (PAC-2 Standards Layer: ACCEPTED). Operational.

### O5: Governance Releases

| Domain | Analysis |
|---|---|
| **Problem** | PAC-1 and PAC-2 are release vehicles, but there is no definition of what a "governance release" is — what it contains, how it's accepted, what "done" means. |
| **Expected outcome** | A release model that bundles related governance decisions, standards, and PG resolutions into a coherent release artifact. |
| **Long-term stability** | Release cadence may be project-driven; release structure should be stable. |
| **Future extensibility** | Medium — PAC-3, PAC-4, etc. |

**Verdict**: Governance Releases are required for PAC-2 closure (how do we know PAC-2 is done?) but are not a distinct PG item. GS-01 lifecycle + GS-01 WP-07 acceptance = release.

---

## Phase 2 — Capability Identification

| # | Capability | Purpose | Inputs | Outputs | Primary Consumers | Lifecycle | Stability | Change Frequency |
|---|---|---|---|---|---|---|---|---|
| C1 | **Project Identity** | Define what ResourceHub/Rule IDE is and their relationship | Stakeholder input, PAC-1 Charter, Project Brief | Identity definition document (RULE_IDE_SCOPE.md or ADR) | All governance docs, roadmap, external communication | One-time decision | Very High | Never (after decision) |
| C2 | **Versioning** | Define version schemes, M↔v mapping, v1.0 criteria | Git tags, milestone history, governance doc versions | VERSIONING.md | All documents, automation scripts, standards | Recurring (per major release) | High | Rarely |
| C3 | **Architecture Documentation** | Maintain accurate ARCHITECTURE.md | Codebase, package inventory, module analysis | Updated ARCHITECTURE.md | Developers, AI agents, onboarding | Continuous | Medium | Per milestone |
| C4 | **Decision Records** | Create and maintain ADRs | Design discussions, architecture reviews, governance decisions | ADR entries in DECISION_LOG.md | Developers, governance | Per decision | High | Per decision |
| C5 | **AI Documentation** | Maintain AI-facing documentation (AI_HANDOFF, AI_MEMORY_PACK, etc.) | Repository state, milestone completions, agent findings | Updated AI docs | AI agents, developers | Per milestone | Medium | Per milestone |
| C6 | **Milestone Planning** | Maintain NEXT_MILESTONE.md with accurate priorities | Completed milestones, new PG items, roadmap | Updated NEXT_MILESTONE.md | Project management, AI agents | Per milestone | Medium | Per milestone |
| C7 | **Documentation Standards** | Maintain AGENTS.md rules and CHANGELOG clarity | Rule changes, changelog events | Updated AGENTS.md, CHANGELOG_AI.md | Developers, AI agents | Continuous | High | Low |
| C8 | **Document Lifecycle** | Deprecate, archive, or clean up stale documents | Stale document inventory (from G-11) | Deprecated/archived documents | Repository maintainers | Per document | High | Per cleanup cycle |
| C9 | **Registry** | Register and track governance objects | New governance documents | Updated Governance Object Registry | Governance, validation scripts | Per document | High | Per document creation |
| C10 | **Review** | Conduct Assessment, Design, and Validation reviews | Work products (assessments, designs, implementations) | Review documents with decisions | Governance projects | Per WP | High | Per review |

---

## Phase 3 — Capability Dependency Analysis

```
                    ┌─────────────────────────┐
                    │   C2: Versioning (P0)    │ ← Foundational
                    └───────────┬─────────────┘
                                │ depends_on
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
    ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
    │ C3: Arch Doc  │   │ C4: ADRs      │   │ C5: AI Docs   │
    │ (PG-03)       │   │ (PG-04)       │   │ (PG-06)       │
    └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
            │                   │                   │
            └───────────────────┼───────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   C1: Identity (ADR)    │ ← One-time decision
                    └─────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ C6: Milestone Planning  │
                    │ (PG-07)                 │
                    └─────────────────────────┘

    ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
    │ C7: Doc Stds  │   │ C8: Lifecycle │   │ C9: Registry  │
    │ (PG-08/09)    │   │ (PG-10)       │   │ (PG-02 DONE)  │
    └───────────────┘   └───────────────┘   └───────────────┘
         Independent          Independent        Independent
```

### Dependency Table

| From | To | Type | Rationale |
|---|---|---|---|
| C3 (Arch) | C2 (Versioning) | Mandatory | ARCHITECTURE.md version references must follow versioning policy |
| C4 (ADR) | C2 (Versioning) | Mandatory | ADRs carry version numbers |
| C5 (AI Docs) | C2 (Versioning) | Mandatory | AI_HANDOFF, NEXT_MILESTONE all reference versions |
| C6 (Milestones) | C1 (Identity) | Optional | Milestone priorities may depend on identity decision |
| C6 (Milestones) | C5 (AI Docs) | Mandatory | NEXT_MILESTONE is itself an AI doc |
| C1 (Identity) | C4 (ADR) | Mandatory | Identity decision is recorded as an ADR |
| C10 (Review) | C9 (Registry) | Mandatory | Review documents must be registered |

**Foundational capabilities**: C2 (Versioning), C9 (Registry), C10 (Review/Standards)
**Dependent capabilities**: C3, C4, C5, C6
**One-time**: C1 (Identity)

---

## Phase 4 — Capability Boundary Review

### C1: Project Identity

| Criterion | Assessment |
|---|---|
| Independent concern? | ✅ Yes — distinct from versioning, architecture, documentation |
| Merge? | ❌ Not with versioning — different lifecycle (one-time vs recurring) |
| Separate? | N/A — already independent |
| Defer? | ❌ Must be resolved — affects naming, architecture, roadmap |
| Reassign? | ⚠️ From PG-01 (governance project) → ADR (decision record) |

**Recommendation**: C1 is a DECISION, not a GOVERNANCE PROJECT. It should not consume a PG slot. It should be handled as an ADR (Decision complexity per GS-01 §3): WP-03 (design options) → WP-04 (stakeholder review) → WP-05 (document) → WP-07 (accept). This is 4 WPs, not 7.

### C2: Versioning

| Criterion | Assessment |
|---|---|
| Independent concern? | ✅ Yes — foundational, no other capability does this |
| Merge? | ❌ Not with identity — identity is one-time; versioning is recurring |
| Separate? | N/A — already independent |
| Defer? | ❌ Cannot defer — P0, blocks all consistency work |
| Reassign? | ✅ Consolidate to PG-05 only. Remove versioning scope from PG-01. |

**Recommendation**: PG-05 OWNS versioning. PG-01 assessment (currently about versioning) is mislabeled — it's a PG-05 assessment.

### C3: Architecture Documentation (PG-03)

| Criterion | Assessment |
|---|---|
| Independent concern? | ✅ Yes — distinct from all other capabilities |
| Boundary clear? | ✅ Update one file (ARCHITECTURE.md) with package inventory |
| Merge? | ❌ No |
| Defer? | ❌ P1 — needed before roadmap decisions |

**Recommendation**: Maintain as PG-03. Scope is clear.

### C4: Decision Records (PG-04)

| Criterion | Assessment |
|---|---|
| Independent concern? | ✅ Yes — ADR creation/review workflow |
| Boundary clear? | ✅ Create ADR-007 and ADR-008 |
| Merge? | ❌ No |

**Recommendation**: Maintain as PG-04. Scope is clear.

### C5: AI Documentation (PG-06)

| Criterion | Assessment |
|---|---|
| Independent concern? | ✅ Yes — AI docs serve a distinct consumer |
| Boundary clear? | ✅ AI_HANDOFF.md and related files |
| Merge? | ❌ No |

**Recommendation**: Maintain as PG-06.

### C6: Milestone Planning (PG-07)

| Criterion | Assessment |
|---|---|
| Independent concern? | ✅ Yes — distinct from AI docs (even though NEXT_MILESTONE is in docs/AI/) |
| Boundary clear? | ✅ One file |
| Merge? | ❌ No |

**Recommendation**: Maintain as PG-07.

### C7: Documentation Standards (PG-08, PG-09)

| Criterion | Assessment |
|---|---|
| Independent concern? | ⚠️ Overlapping — both are minor documentation fixes |
| Merge? | ✅ Merge PG-08 and PG-09 into one project: "Documentation Standards Maintenance" |
| Why merge? | Both are P3, both touch reference documents, both are single-commit fixes, both are independent of other PG items |

**Recommendation**: Merge PG-08 + PG-09. Combined scope: (a) add `add_suffix` row to AGENTS.md, (b) clarify CHANGELOG_AI.md M8 entries.

### C8: Document Lifecycle (PG-10)

| Criterion | Assessment |
|---|---|
| Independent concern? | ✅ Yes — deprecation is a distinct lifecycle stage |
| Boundary clear? | ✅ One file to deprecate |
| Merge? | ❌ No |

**Recommendation**: Maintain as PG-10.

### C9: Registry (PG-02)

**Status**: DONE. Operational. No changes.

### C10: Review / Standards

**Status**: DONE (PAC-2 Standards Layer: ACCEPTED). Operational.

---

## Phase 5 — Governance Project Mapping

### Recommended Architecture

| PG | Capability | Complexity | Priority | Status |
|---|---|---|---|---|
| PG-01 | **C1: Project Identity** — Define Rule IDE relationship to ResourceHub | Decision (4 WPs) | P1 | Not started |
| PG-02 | C9: Registry — Governance Object Index | ✅ COMPLETED | — | ACCEPTED |
| PG-03 | C3: Architecture Documentation | Document | P1 | Pending |
| PG-04 | C4: Decision Records (ADR-007, ADR-008) | Document | P1 | Pending |
| PG-05 | **C2: Versioning** — Versioning policy, M↔v mapping, v1.0 criteria | Full (7 WPs) | P0 | WP-01 done (assessment exists, mislabeled as PG-01) |
| PG-06 | C5: AI Documentation | Document | P0 | Pending |
| PG-07 | C6: Milestone Planning | Document | P0 | Pending |
| PG-08 | C7: Documentation Standards (merged PG-08 + PG-09) | Amendment | P3 | Pending |
| PG-09 | *(merged into PG-08)* | — | — | — |
| PG-10 | C8: Document Lifecycle | Document | P2 | Pending |

### Explicit Evaluation: PG-01

| Question | Answer |
|---|---|
| Current scope | "Governance Versioning Framework" (per PG-01 Assessment) — **wrong domain** |
| Correct scope | "Project Identity" — Define Rule IDE relationship to ResourceHub |
| Is PG-01 a governance project? | **No.** It's a decision. It produces one artifact, not an ongoing capability. |
| Does PG-01 need 7 WPs? | **No.** Use Decision complexity: WP-03 (options) → WP-04 (review) → WP-05 (ADR) → WP-07 (acceptance). |
| Does PG-01 currently contain versioning? | **Yes — incorrectly.** The assessment is about versioning. This is PG-05's domain. |

**Recommendation for PG-01**:
1. Remove versioning scope — this belongs to PG-05
2. Reclassify as Decision complexity (4 WPs, not 7)
3. Define scope: produce RULE_IDE_SCOPE.md or ADR-nnn documenting the ResourceHub↔Rule IDE relationship
4. WP-03 produces 3 options with tradeoffs (per PAC-2 Charter risk R1)

### Explicit Evaluation: PG-05

| Question | Answer |
|---|---|
| Current scope | "Normalize version references + define versioning policy" (PAC-2 Charter) |
| PG-01 Assessment content | Governance Versioning — version identification, lifecycle tracking, naming conventions, cross-reference integrity |
| Is PG-01 Assessment about versioning? | **Yes.** Every finding is about versioning. The assessment self-references PG-05 as the intended consumer. |
| Does PG-05 own versioning architecturally? | **Yes.** Versioning is a foundational capability (C2) that all other capabilities depend on. |

**Recommendation for PG-05**:
1. Accept the existing PG-01 Assessment (`GOV-REV-005`) as PG-05 WP-01
2. Re-label metadata: `part_of: PG-05`, title: "PG-05 WP-01..."
3. Proceed to WP-02 (Assessment Review)
4. This is the highest-priority PG item — it blocks all consistency work

---

## Phase 6 — Future Architecture Validation

### PG-03 through PG-10 Fit

| PG | Capability | Fits proposed architecture? | Notes |
|---|---|---|---|
| PG-03 | Architecture docs | ✅ | Independent, well-scoped |
| PG-04 | ADRs | ✅ | Independent, well-scoped |
| PG-06 | AI docs | ✅ | Independent; blocked by PG-05 (versioning) |
| PG-07 | Milestones | ✅ | Independent; blocked by PG-05 |
| PG-08 | Doc standards (merged) | ✅ | Independent, low-priority |
| PG-10 | Lifecycle | ✅ | Independent; blocked by PG-05 |

### Governance Releases

| Aspect | Architecture Position |
|---|---|
| What is a release? | A release is the closure of a PAC phase. PAC-2 closes when all PG items are accepted. |
| Release artifact | Governance Acceptance record for the PAC phase (GOV-REC-XXX) |
| Release governance | GS-01 WP-07 (Acceptance) is the release mechanism |
| No new capability needed | Release is a lifecycle event, not a separate capability |

### Backward Compatibility

| Baseline | Impact |
|---|---|
| PAC-1 Accepted v1.0 | ✅ Zero impact — no PG identifier changes, no document modifications |
| PG-02 completed artifacts | ✅ Zero impact |
| PAC-2 Standards | ✅ Zero impact — all 5 standards remain in force |
| Registry | ✅ Gov-REV-005 re-labeled from PG-01 to PG-05 (metadata update, not scope change) |

### Scalability

| Scenario | Architecture Response |
|---|---|
| PG-11+ identified (PAC-3) | PG-11+ follows the same PG-NN identifier pattern |
| New standard needed (GS-06) | GS-06 follows GS-01 lifecycle + GS-04 naming |
| Versioning policy needs revision | PG-05 defines the policy; revision follows 7-WP cycle or Amendment complexity |
| Registry outgrows single file | Split into Type Registries (REC Registry, REV Registry, etc.) — backward compatible |

---

## Decision Options

### Option A (Recommended): Reclassify PG-01 as ADR + Re-label Assessment to PG-05

| Action | Impact |
|---|---|
| PG-01 scope → Project Identity (ADR) | One-time decision, 4 WPs, not a full governance project |
| PG-01 Assessment → PG-05 WP-01 | Assessment content matches versioning domain |
| PG-05 owns versioning exclusively | Single owner, clear accountability |
| PG-05 starts at WP-02 | Assessment review is next step |

**Evaluation against decision criteria**:

| Criterion | Score |
|---|---|
| Clear capability ownership | ✅ PG-01 = Identity, PG-05 = Versioning — no overlap |
| Low coupling | ✅ Identity and Versioning are independent |
| High cohesion | ✅ Each PG has one capability |
| Stable long-term evolution | ✅ New decisions are ADRs; new capabilities are PGs |
| Minimal governance overlap | ✅ Zero overlap between PG-01 and PG-05 |
| Minimal future migration cost | ✅ Re-label one document ($0); PG-01 never started |
| Strong traceability | ✅ PG-01 ADR traces to PAC-2 Charter; PG-05 traces to PAC-1 Resolution |
| Alignment with objectives | ✅ Both Identity and Versioning objectives met |

### Option B: PG-01 Absorbs Versioning, PG-05 Removed

| Action | Impact |
|---|---|
| PG-01 = Governance Versioning (current de facto) | PG-05 becomes empty/null |
| PG-05 scope → PG-01 | One PG item owns all versioning |

**Evaluation**:

| Criterion | Assessment |
|---|---|
| Clear ownership | ✅ Single owner — but PG-01 originally meant Identity, losing that scope |
| Low coupling | ⚠️ Versioning depends on nothing; Identity depends on Versioning |
| Historical clarity | ❌ PG-01 now means two different things across PAC-1 and PAC-2 |

### Option C: PG-01 Stays as Is (Two Versioning Projects)

No change. PG-01 and PG-05 both defined as versioning.

**Evaluation**:

| Criterion | Assessment |
|---|---|
| Clear ownership | ❌ Two projects claim versioning |
| Low coupling | ❌ PG-01 and PG-05 are coupled by scope overlap |
| Governance overlap | ❌ Direct overlap on versioning |
| Future migration cost | ❌ High — must resolve the conflict eventually |

---

## Recommended Architecture

```
PAC-2 Governance Capabilities

┌─────────────────────────────────────────────────────────┐
│ FOUNDATIONAL (P0)                                       │
│                                                         │
│  PG-05: Versioning Policy [Full, 7 WPs]                 │
│    └─ Input: PG-01 Assessment (re-label from PG-01)     │
│    └─ Output: VERSIONING.md                             │
│                                                         │
│  PG-06: AI Documentation [Document]                     │
│    └─ Output: AI_HANDOFF.md, AI_MEMORY_PACK.md          │
│                                                         │
│  PG-07: Milestone Planning [Document]                   │
│    └─ Output: NEXT_MILESTONE.md                         │
├─────────────────────────────────────────────────────────┤
│ STRUCTURAL (P1)                                         │
│                                                         │
│  PG-01: Project Identity [Decision, 4 WPs]              │
│    └─ Output: ADR-nnn or RULE_IDE_SCOPE.md              │
│                                                         │
│  PG-03: Architecture Documentation [Document]           │
│    └─ Output: ARCHITECTURE.md                           │
│                                                         │
│  PG-04: Decision Records [Document]                     │
│    └─ Output: ADR-007, ADR-008                          │
├─────────────────────────────────────────────────────────┤
│ MAINTENANCE (P2–P3)                                     │
│                                                         │
│  PG-08: Documentation Standards [Amendment]             │
│    └─ Output: AGENTS.md + CHANGELOG_AI.md updates       │
│                                                         │
│  PG-10: Document Lifecycle [Document]                   │
│    └─ Output: Deprecate development/current_status.md   │
├─────────────────────────────────────────────────────────┤
│ COMPLETED                                               │
│                                                         │
│  PG-02: Governance Object Index ✅                      │
│  PAC-2 Standards Layer ✅                                │
└─────────────────────────────────────────────────────────┘
```

---

## Risks

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R1 | PG-01 reclassification is rejected | Low | PG-01 as a full project is heavy for a one-time decision; ADR is more appropriate |
| R2 | PG-05 Assessment re-label breaks registry | Low | One metadata field change (`part_of: PG-01` → `part_of: PG-05`); registry reflects actual content |
| R3 | PG-08/09 merger creates scope confusion | Low | Both are P3, independent, single-commit changes; combined scope is simpler |
| R4 | Stakeholder objects to PG-01 being an ADR | Medium | PG-01 requires human stakeholder decision regardless of format; ADR is the format for decisions |

---

## Trade-offs

| Trade-off | Chosen | Rationale |
|---|---|---|
| PG-01 as project vs ADR | ADR | One-time decision with no recurring lifecycle |
| PG-05 as sole versioning owner vs shared | Sole owner | Versioning is foundational; split ownership creates deadlock |
| PG-08/PG-09 merged vs separate | Merged | Both P3, both small, both independent |

---

## Final Recommendation

1. **Re-label `GOV-REV-005`** from PG-01 to PG-05 — the assessment content is versioning
2. **Reclassify PG-01** from Full governance project to Decision complexity (ADR)
3. **Consolidate versioning** under PG-05 — single owner for foundational capability
4. **Merge PG-08 + PG-09** — combined Documentation Standards maintenance
5. **Proceed with PG-05 WP-02** — Assessment Review is the highest-priority next step

**Historical document assignments do not outweigh architecture quality. The current PG-01/PG-05 scope conflict is a labeling error, not a design decision. Correcting it now avoids compounding the error through 6 more WPs.**
