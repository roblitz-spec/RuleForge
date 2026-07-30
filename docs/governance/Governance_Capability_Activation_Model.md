# Governance Capability Activation Model v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-GUIDE-009` | `GUIDE` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-GUIDE-008` (GOM-001) | PAC-2 Governance |

---

**Date**: 2026-07-29 | **Type**: Governance Capability Activation Model | **Status**: Draft for review

---

## 1. Purpose

Define when governance capabilities become operationally required based on organizational scale and governance criticality. This model prevents both premature governance complexity (over-engineering for small projects) and late governance formalization (under-governing critical systems).

---

## 2. Governance Activation Principle

> Governance capabilities are progressively activated based on organizational scale and governance criticality rather than universally enforced from inception.

**The objective**: Maintain governance proportionality while preserving future scalability. A single-maintainer project does not need enterprise release governance. A regulated environment does not operate with ad-hoc processes.

---

## 3. Activation Dimensions

### 3.1 Dimension A — Scale

| # | Indicator | Measurement |
|---|---|---|
| S1 | Number of Governance Projects (PG items) | Active + completed PG items in current PAC phase |
| S2 | Number of active governance contributors | Distinct authors of governance artifacts in current PAC phase |
| S3 | Number of governance artifacts | Total registered governance objects (registry count) |
| S4 | Number of concurrent governance changes | Open PG items + active CAR/CMP cycles |
| S5 | Governance release frequency | PAC phases per calendar year |
| S6 | Number of governance programs | Distinct governance programs (PAC, standards, compliance, etc.) |

### 3.2 Scale Thresholds

| Level | PG Items | Contributors | Artifacts | Concurrent Changes | Release Frequency | Programs |
|---|---|---|---|---|---|---|
| **Small** | ≤5 active | 1–2 | ≤50 | ≤2 | ≤1/year | 1 |
| **Growth** | 6–15 active | 3–5 | 51–150 | 3–5 | 2/year | 2 |
| **Enterprise** | >15 active | >5 | >150 | >5 | >2/year | ≥3 |

**Current ResourceHub assessment**: Small — 8 pending PG items (≤5 active at a time), 1–2 contributors, 50 artifacts, 2 concurrent CAR/CMP cycles, ≤1 PAC phase/year, 1 governance program (PAC).

### 3.3 Threshold Adjustability

Thresholds are evidence-based guidelines, not hard cutoffs. A project at 6 active PG items with a single maintainer may still operate at Small scale if governance complexity remains low. Thresholds should be reviewed at each PAC phase boundary.

---

## 4. Dimension B — Criticality

### 4.1 Criticality Indicators

| # | Indicator | Question |
|---|---|---|
| C1 | External audit requirements | Is governance subject to external audit? |
| C2 | Regulatory obligations | Are there regulatory requirements for governance documentation? |
| C3 | Contractual commitments | Do contracts require specific governance controls? |
| C4 | Legal traceability | Must governance decisions be legally traceable? |
| C5 | Safety implications | Can governance failures cause safety issues? |
| C6 | Compliance obligations | Are there compliance frameworks that apply? |
| C7 | Executive oversight | Is there executive governance oversight? |

### 4.2 Criticality Levels

| Level | Indicators | Description |
|---|---|---|
| **Low** | None of C1–C7 apply | Internal project governance; no external accountability |
| **Moderate** | 1–2 of C1–C7 apply | Some external accountability; basic traceability required |
| **High** | 3–4 of C1–C7 apply | Significant external accountability; formal governance required |
| **Mission-Critical** | 5+ of C1–C7 apply | Full governance framework required; regulatory non-compliance is consequential |

**Current ResourceHub assessment**: Low — internal project, no regulatory obligations, no external audit, no contractual governance requirements.

---

## 5. Capability Classification

### 5.1 Core Capabilities (Always Required)

Core capabilities are the minimum viable governance foundation. They are required at all scale and criticality levels.

| # | Capability | Purpose | Minimum Requirement | Justification |
|---|---|---|---|---|
| **CORE-1** | Evidence Management | Maintain repository of governance evidence | Git repository with committed artifacts | Without evidence, governance decisions are unverifiable. P1 (Evidence Before Decision) is universally applicable. |
| **CORE-2** | Governance Registry | Track governance objects and their relationships | `Governance_Object_Registry.md` with GOV-IDs | Without a registry, traceability is impossible. GS-05 requires explicit relationship declarations. |
| **CORE-3** | Basic Traceability | Declare primary source and part_of relationships | `primary_source` and `part_of` metadata fields | Every governance object must be traceable to its source. Minimum GS-05 compliance. |
| **CORE-4** | Governance Standards | Define document structure, naming, review process | GS-01 through GS-05 (PAC-2 Standards) | Standards prevent chaos. Without them, every project reinvents governance formats. |
| **CORE-5** | Decision Records | Record governance decisions | ADR entries with rationale | Decisions without records are oral history. P6 (Every Change Traceable) applies universally. |
| **CORE-6** | Document Lifecycle | Track document status from draft to accepted | GS-02 §5 lifecycle stages | Without lifecycle tracking, consumers don't know what's operational. |

### 5.2 Growth Capabilities (Conditionally Activated)

Growth capabilities activate when scale or criticality reaches defined thresholds. They add structure without enterprise overhead.

| # | Capability | Purpose | Activation Trigger | Scale Threshold | Criticality Threshold |
|---|---|---|---|---|---|
| **GROW-1** | Capability Architecture Review (CAR) | Formal architecture analysis for governance changes | Scope conflict or capability ambiguity exists | Growth (≥6 active PG items) | Moderate |
| **GROW-2** | Capability Migration Planning (CMP) | Structured migration plan for capability changes | CAR identifies migration needed | Growth | Moderate |
| **GROW-3** | Formal Governance Reviews | Structured review process per GS-03 | GS-01 WP-02, WP-04, WP-06 | Growth | Moderate |
| **GROW-4** | Structured Release Governance | Formal release acceptance process | PAC phase closure requires baseline declaration | Growth | Moderate |
| **GROW-5** | Scope Decision Review (SDR) | Formal scope determination for governance issues | Multiple PG items interact or scope is contested | Growth | Moderate |
| **GROW-6** | Evolution Approval Review (EAR) | Formal approval gate before implementation | CAR + CMP produced; implementation pending | Growth | Moderate |

**Benefits**: Prevents ad-hoc governance evolution. Ensures architecture decisions are explicit and reviewed.

**Risks if delayed**: Capability overlap goes undetected. Scope conflicts compound. Governance debt accumulates.

### 5.3 Enterprise Capabilities (Enterprise Only)

Enterprise capabilities activate only under substantial governance complexity. They add formal controls appropriate for regulated or multi-team environments.

| # | Capability | Purpose | Activation Trigger | Scale Threshold | Criticality Threshold |
|---|---|---|---|---|---|
| **ENT-1** | Implementation Contract (IC) | Formal, signed-off implementation specification | Implementation spans multiple repositories or teams | Enterprise | High |
| **ENT-2** | Advanced Separation of Duties | Distinct Governance Reviewer, Architect, and Maintainer roles | Conflict of interest risk exists in review chain | Enterprise | High |
| **ENT-3** | Formal Approval Boards | Multi-stakeholder governance approval body | Decisions require cross-team consensus | Enterprise | High |
| **ENT-4** | Enterprise Release Governance | Multi-stage release with staging, sign-off, and rollback planning | Releases affect external consumers or contracts | Enterprise | Mission-Critical |
| **ENT-5** | Governance Metrics Dashboard | Automated tracking of governance KPIs | Governance health must be continuously monitored | Enterprise | High |
| **ENT-6** | Compliance Audit Trail | Immutable, timestamped audit log of governance decisions | Regulatory or contractual audit requirements exist | Enterprise | Mission-Critical |

**Benefits**: Full governance accountability. Regulatory compliance. Multi-stakeholder governance.

**Risks if adopted prematurely**: Governance paralysis — process consumes more effort than the work being governed. Single maintainer operating approval boards is governance theater. Overhead cost exceeds governance benefit.

**Risks if adopted too late**: Regulatory non-compliance. Audit failure. Loss of stakeholder trust. Governance decisions challenged due to lack of process.

---

## 6. Capability Activation Matrix

| Capability | Small + Low | Small + Moderate | Growth + Low | Growth + Moderate | Enterprise + High | Enterprise + Mission-Critical |
|---|---|---|---|---|---|---|
| Evidence Management | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core |
| Governance Registry | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core |
| Basic Traceability | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core |
| Governance Standards | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core |
| Decision Records | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core |
| Document Lifecycle | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core | ✅ Core |
| Capability Architecture Review | — | ⚠️ Activated | — | ✅ Activated | ✅ Activated | ✅ Activated |
| Capability Migration Planning | — | ⚠️ Activated | — | ✅ Activated | ✅ Activated | ✅ Activated |
| Formal Governance Reviews | — | — | — | ✅ Activated | ✅ Activated | ✅ Activated |
| Structured Release Governance | — | — | — | ✅ Activated | ✅ Activated | ✅ Activated |
| Scope Decision Review | — | — | — | ✅ Activated | ✅ Activated | ✅ Activated |
| Evolution Approval Review | — | — | — | ✅ Activated | ✅ Activated | ✅ Activated |
| Implementation Contract | — | — | — | — | ✅ Activated | ✅ Activated |
| Advanced Separation of Duties | — | — | — | — | — | ✅ Activated |
| Formal Approval Boards | — | — | — | — | — | ✅ Activated |
| Enterprise Release Governance | — | — | — | — | — | ✅ Activated |
| Governance Metrics Dashboard | — | — | — | — | ✅ Activated | ✅ Activated |
| Compliance Audit Trail | — | — | — | — | — | ✅ Activated |

**Legend**:
- ✅ Core = always active
- ✅ Activated = activated at this threshold
- ⚠️ Activated = conditionally activated (per scenario judgment)
- — = not required; activating prematurely is a governance anti-pattern

---

## 7. Governance Scenarios

### Scenario A: Single Maintainer, Single Program, Low Criticality

**Profile**: ResourceHub today. 1–2 contributors, 50 artifacts, 8 pending PG items, no external accountability.

| Category | Capabilities |
|---|---|
| **Required** | Core: Evidence Management, Registry, Basic Traceability, Governance Standards, Decision Records, Document Lifecycle |
| **Optional** | CAR (only when scope conflicts arise — as demonstrated by PG-01/PG-05), CMP (only when CAR identifies migration), GS-03 reviews (Full complexity PG items only) |
| **Deferred** | SDR (single maintainer resolves scope directly), EAR (single reviewer suffices), IC (implementation scope is clear from CMP), all Enterprise capabilities |

**Rationale**: Single maintainer is the Governance Sponsor, Architect, Reviewer, Maintainer, Release Authority, and Decision Authority. Formal separation of duties and approval boards add ceremony without adding governance quality. CAR/CMP are activated only when capability boundaries need formal analysis — not for every PG item.

### Scenario B: Multiple Maintainers, Growing Governance Portfolio

**Profile**: 3–5 contributors, 80 artifacts, 10 active PG items, occasional external stakeholders.

| Category | Capabilities |
|---|---|
| **Required** | All Core + SDR, CAR, CMP, Formal Governance Reviews (GS-03), Structured Release Governance |
| **Optional** | EAR (formal approval gate for multi-maintainer changes), IC (for cross-repository changes) |
| **Deferred** | All Enterprise capabilities |

**Rationale**: Multiple maintainers create coordination overhead. SDR prevents scope disputes. Formal reviews (GS-03) ensure consistency across contributors. Structured release governance formalizes baseline acceptance.

### Scenario C: Multi-Program Governance

**Profile**: 5+ contributors, 150+ artifacts, multiple governance programs (PAC + standards + compliance), significant external communication.

| Category | Capabilities |
|---|---|
| **Required** | All Core + all Growth + EAR, IC |
| **Optional** | Advanced Separation of Duties (reviewer ≠ author per GS-03 §10 C2 is sufficient at this scale) |
| **Deferred** | Formal Approval Boards, Enterprise Release Governance (unless Mission-Critical), Compliance Audit Trail |

**Rationale**: Multi-program governance requires formal coordination. EAR and IC ensure that changes are approved and specified before execution. Separation of duties becomes important but GS-03's existing constraint (reviewer ≠ author) is sufficient.

### Scenario D: Regulated Environment, High Audit Requirements

**Profile**: Any scale + Mission-Critical criticality. External audits, regulatory obligations, contractual governance requirements.

| Category | Capabilities |
|---|---|
| **Required** | All Core + all Growth + all Enterprise |
| **Optional** | None — Mission-Critical requires full governance |
| **Deferred** | None |

**Rationale**: Regulatory non-compliance is consequential. Every governance decision must be traceable to an approved architecture, reviewed by an independent party, executed under contract, and auditable. The full GOM lifecycle is mandatory.

---

## 8. GOM Alignment Assessment

### 8.1 GOM Stage Activation by Scale/Criticality

| GOM Stage | Always Active | Conditionally Active | Enterprise Only | Trigger |
|---|---|---|---|---|
| **EI** (Evidence Investigation) | ✅ Core | — | — | P1 (Evidence Before Decision) is universal |
| **SDR** (Scope Decision Review) | — | ✅ Growth | — | Multiple PG items or scope contested |
| **CAR** (Capability Architecture Review) | — | ✅ Growth + Moderate | — | Scope conflict or capability ambiguity |
| **CMP** (Capability Migration Plan) | — | ✅ Growth + Moderate | — | CAR identifies migration |
| **EAR** (Evolution Approval Review) | — | ✅ Growth + Moderate | — | Multi-maintainer or formal governance |
| **ADR** (Architecture Decision Record) | ✅ Core | — | — | P6 (Every Change Traceable) is universal |
| **IC** (Implementation Contract) | — | — | ✅ Enterprise + High | Cross-repository or regulated |
| **Implementation** | ✅ Core | — | — | All governance changes require implementation |
| **Validation** | ✅ Core (basic) | ✅ Growth (formal) | — | Basic: self-review. Formal: GS-03 R3 |
| **GR** (Governance Release) | ✅ Core (per PAC) | ✅ Growth (structured) | — | Core: acceptance record. Growth: formal process |
| **Registry Sync** | ✅ Core | — | — | Registry must reflect repository state |

### 8.2 GOM Role Activation

| Role | Small + Low | Growth + Moderate | Enterprise + High |
|---|---|---|---|
| Governance Sponsor | Single maintainer | Designated lead | Formal appointment |
| Governance Architect | Single maintainer | Designated role (may be same person as Sponsor) | Distinct role |
| Governance Reviewer | Self-review or peer | Designated reviewer (≠ author) | Independent reviewer (GS-03 §10 C2) |
| Repository Maintainer | Single maintainer | Designated role | Distinct role |
| Release Authority | Single maintainer | Designated lead | Independent authority |
| Decision Authority | Single maintainer | Governance Sponsor + Architect | Formal board or designated authority |

### 8.3 Alignment Verdict

| Aspect | Assessment |
|---|---|
| GOM is compatible with progressive activation? | ✅ Yes — GOM stages are capability definitions, not universal mandates. GCAM defines when each stage is activated. |
| GOM roles scale with complexity? | ✅ Yes — role consolidation at Small scale is documented; separation at Enterprise is explicit. |
| GOM gates remain blocking? | ✅ Yes — activated gates are blocking. Inactive gates are not applicable (no gate → no block). |
| Core capabilities meet minimum GOM requirements? | ✅ Yes — EI + ADR + Implementation + Validation + Registry form the minimum governance cycle. |

---

## 9. Progressive Activation Guidance

### 9.1 Current ResourceHub Activation

| State | Value |
|---|---|
| Scale | **Small** — 1–2 contributors, 50 artifacts, 8 pending PG items |
| Criticality | **Low** — no external audit, regulation, contract, or compliance obligations |
| Activated | **Core only** + conditional CAR/CMP (as demonstrated by CAR-001/CMP-001) |
| Deferred | SDR, EAR, IC, all Enterprise capabilities |

**Current Governance Posture**: Lightweight but complete. Core capabilities provide the governance foundation. CAR/CMP are activated on-demand when capability boundaries are unclear. This is appropriate for the current scale and criticality.

### 9.2 Activation Triggers

| Trigger | When | Action |
|---|---|---|
| Scale reaches Growth (≥6 active PG items) | PAC-3 or PAC-4 if PG count grows | Activate SDR, formal reviews, structured release governance |
| Criticality reaches Moderate | External audit, contract, or regulatory requirement | Activate EAR, formal validation |
| Scale reaches Enterprise | Multi-team, 150+ artifacts | Activate IC, separation of duties, metrics |
| Criticality reaches Mission-Critical | Regulated environment | Activate all Enterprise capabilities |

### 9.3 Deactivation

Capabilities are never deactivated once activated. A project that reaches Growth scale does not revert to Small activation even if PG count decreases. The capability remains available; its use may reduce.

---

## 10. Constraints

| # | Constraint |
|---|---|
| C1 | GCAM defines activation, not redesign — GOM stages and GS standards remain as defined |
| C2 | Core capabilities are non-negotiable; a project with zero evidence management is not governed |
| C3 | Enterprise capabilities activated prematurely are governance anti-patterns — process without purpose |
| C4 | Criticality overrides scale — Mission-Critical at Small scale activates Enterprise capabilities |
| C5 | Thresholds are guidelines, not hard cutoffs — use judgment for borderline cases |

---

## 11. Evidence References

| Precedent | What It Proves |
|---|---|
| CAR-001 (`GOV-REV-015`) | CAR was activated on-demand for PG-01/PG-05 scope conflict — not for every PG item. This validates the "conditional activation" model. |
| CMP-001 (`GOV-REV-016`) | CMP followed CAR naturally — activation was proportional to the governance issue, not mandated for all changes. |
| GOM-001 (`GOV-GUIDE-008`) | 12-stage GOM lifecycle; GCAM defines activation conditions for each stage. |
| PAC-2 Standards | Core capabilities (GS-01–GS-05) are in force; GCAM does not modify them. |
| PAC-2 Charter | 10 PG items defined; GCAM's "Small" scale assessment is consistent with current project scope. |

---

**Governance Capability Activation Model defined. Governance complexity is proportional to need.**
