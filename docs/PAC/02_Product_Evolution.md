# 02 — Product Evolution

**PAC-1 Discovery | Date: 2026-07-24**

Sources: Git log, `AGENTS.md`, `docs/AI/CHANGELOG_AI.md`, `docs/AI/PROJECT_BRIEF.md`, `docs/AI/DECISION_LOG.md`, commit messages.

---

## Stage 1 — Problem

**What**: Windows users need to batch-rename files with preview safety.

**Evidence** (MEDIUM):
- `README.md`: "Windows 桌面批量重命名工具" — no deeper problem statement documented.
- No user research or problem definition in repository.

**Confidence**: MEDIUM (inferred from solution)

---

## Stage 2 — Initial Solution (M2–M5)

**What**: Core rename pipeline with basic rules and safety guarantees.

**When**: Earliest commits: `49bb3f9` (M2) → `920de63` (M5).

**Milestones**: M2 (EditSession, WorkingCopy), M3 (Commit, Undo/Redo, Preview Isolation), M4 (Auto Save, Session Persistence), M4.1 (Architecture Alignment), M5 (Smart Previews & Analysis Warnings, 356 tests).

**Evidence** (HIGH): Git tags `M2-complete` through `M5-complete`. Commit messages.

**Major Capability**: Foundation — undo, preview, basic RuleStep types (replace, case, trim).

---

## Stage 3 — Rule Generation (M12–M14)

**What**: Transformational rule types for structured renaming.

**When**: Tagged in earlier branch, merged into `m10-phase3a-rule-analysis`.

**Milestones**: M12 (Number Rule, 122 tests), M13 (Insert Rule, 131 tests), M14 (Date Rule + MetadataProvider, 144 tests).

**Evidence** (HIGH): Git tags `M12-complete`, `M13-complete`, `M14-complete`. `AGENTS.md` baseline table. ADR-004 (RuleEngine pure function), ADR-005 (Context Contract).

**Architectural Shift**: RuleEngine became a pure-function framework with context dict for state. `RuleAnalysis` module introduced for dependency analysis.

---

## Stage 4 — Rule Management (M15–M16, M6–M7)

**What**: Rule lifecycle management, CRUD, governance.

**When**: M15–M16 (earlier branch) + M6–M7 (current branch).

**Milestones**: M15 (AddSuffix Rule, AI Memory v1.0), M16 (AI Memory v2.0 Governance, Selection Features), M6 (Rule Duplication, 384 tests), M7 (Architecture Consolidation & Quality Hardening, 398 tests).

**Evidence** (HIGH): Git tags. `docs/AI/ARCHITECTURE_AUDIT_M4.md`. M6 REVIEW_M6.md. `docs/AI/M6_COMPLETION.md`.

**Architectural Shift**: `editor/` package introduced (`EditSession`, `DomainValidator`). AI Memory governance established (12 source documents, `README_AI.md`). ID generation consolidated (WP-19).

---

## Stage 5 — Rule Platform (M8, M11.2)

**What**: User-facing platform features — presets, sorting, pinning, regex assistant.

**When**: M8 (current branch), M11.2 (earlier branch).

**Milestones**: M8 (Rule Presets, 447 tests), M11.2 (Sortable Table, Context Menu, Pin Rules, Regex Assistant, NAS Performance Fix).

**Evidence** (HIGH): Git tags `M8-complete`, `M11.2-complete`. `docs/AI/M8_COMPLETION.md`. ADR-006 (NAS/SMB performance).

**Architectural Shift**: `PresetStore` as separate persistence layer. `Settings` for startup restoration. Scanner optimized for network filesystems (511× speed improvement).

---

## Stage 6 — Rule IDE (Emerging, Not Formalized)

**What**: Rule-focused editing environment within ResourceHub.

**When**: `editor/` package implemented (M7–M8 timeframe). "Master Design" referenced but not in repo.

**Evidence** (MEDIUM):
- `editor/__init__.py`: `# Editor Core — Rule IDE editing layer (Master Design, Section 3)`
- `editor/domain_validator.py`: `# DomainValidator — ... (Master Design AD-03)`
- `editor/edit_session.py`: `# EditSession — ... (Master Design Section 4.1)`
- `docs/AI/AI_HANDOFF.md`: `"4. Prepare M12 Rule IDE"`
- `docs/AI/CURRENT_STATUS.md` TD-003: trigger "Rule IDE introduces new step types"

**Status**: Partially implemented (382 lines in `editor/` package). No formal rename. No project charter update.

**Confidence**: MEDIUM (implemented code references external design document)

---

## Major Turning Points

| Turning Point | Evidence | When |
|---|---|---|
| **RuleEngine → Pure Function** | ADR-004, AGENTS.md | M12 |
| **Context Contract Frozen** | ADR-005 | M14 |
| **AI Memory Governance v2.0** | README_AI.md, 12 source docs | M16 / M7 |
| **editor/ Package Introduced** | edit_session.py, domain_validator.py | M7–M8 |
| **NAS Performance Crisis** | ADR-006, 511× speed fix | M11.2 |
| **Rule Presets** | PresetStore, preset_manager_dialog.py | M8 |

---

## Architectural Shifts

| Shift | From | To | Evidence |
|---|---|---|---|
| State model | Module-level counters | Context dict from PreviewEngine | ADR-004, ADR-005 |
| Rule type addition | Modify engine core | Register handler + UI entry | `AGENTS.md` § 架构原则 |
| Persistence | Single `rules.json` | Multi-file (rules.json + presets.json) | `storage/preset_store.py` |
| Validation | Embedded in UI | `editor/domain_validator.py` (UI-independent) | Module docstring |
| Scanner | `Path.resolve()` | `Path(entry.path)` direct | ADR-006 |
| AI memory | Chat history dependent | 12-document governance system | `README_AI.md` |

---

## Product Abstraction Shifts

| Shift | Evidence |
|---|---|
| Tool → Platform | Settings persistence, PresetStore, i18n, packaging |
| Editor → IDE | `editor/` package, DomainValidator, EditSession |
| Single-user → Configurable | Presets, Settings, locale selection |

**Current state**: ResourceHub is a desktop application with platform-level features. The Rule IDE transition is emerging from the `editor/` package but has not been formally established.

---

## Evolution Diagram

```
Problem: Manual batch rename on Windows
    │
    ▼
Initial Solution: Core pipeline + basic rules + undo (M2–M5)
    │
    ▼
Rule Generation: Number, Insert, Date, AddSuffix (M12–M16)
    │
    ▼
Rule Management: Duplication, CRUD, Architecture consolidation (M6–M7)
    │
    ▼
Rule Platform: Presets, Sorting, Pinning, Regex, NAS perf (M8, M11.2)
    │
    ▼
Rule IDE: editor/ package, DomainValidator, EditSession (EMERGING)
    └── NOT formalized — no product rename, no charter update
```

---

**Confidence Summary**:

| Stage | Confidence | Basis |
|---|---|---|
| Problem | MEDIUM | Inferred from solution; no explicit problem doc |
| Initial Solution | HIGH | Git tags + commit messages |
| Rule Generation | HIGH | Git tags + ADRs |
| Rule Management | HIGH | Git tags + review docs |
| Rule Platform | HIGH | Git tags + completion reports |
| Rule IDE | MEDIUM | Code + 1 stale planning ref; no formal document |
