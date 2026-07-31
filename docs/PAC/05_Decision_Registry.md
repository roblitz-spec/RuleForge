# 05 — Decision Registry

**PAC-1 Discovery | Date: 2026-07-24**

All decisions extracted from repository evidence. Status: `Confirmed` = documented in ADR or equivalent; `Implied` = inferred from code structure; `Unconfirmed` = insufficient evidence.

---

## Architecture Decisions

### D-01: RuleEngine Pure Function Contract

| Field | Value |
|---|---|
| Decision | RuleEngine handlers are pure functions. State (index, metadata) passed via `context` dict. |
| Status | **Confirmed** (ADR-004) |
| Evidence | `docs/AI/DECISION_LOG.md`, `engine/rule_engine.py` (no module-level state), `AGENTS.md` § 架构原则 |
| Confidence | HIGH |
| Impact | All 10 RuleStep handlers follow this contract. Testable in isolation. Thread-safe. |

### D-02: Context Contract (Frozen Fields)

| Field | Value |
|---|---|
| Decision | `context["index"]`, `context["count"]`, `context["metadata"]` are frozen. New fields allowed; existing cannot be renamed or re-typed. |
| Status | **Confirmed** (ADR-005) |
| Evidence | `docs/AI/DECISION_LOG.md`, `AGENTS.md` § Context Contract |
| Confidence | HIGH |
| Impact | Number Rule, Date Rule, and all future context consumers depend on this. |

### D-03: Avoid Path.resolve() in Scanner

| Field | Value |
|---|---|
| Decision | Scanner hot path must not call `Path.resolve()`, `realpath()`, or per-entry stat. Use `Path(entry.path)` from `os.scandir()`. |
| Status | **Confirmed** (ADR-006) |
| Evidence | `docs/AI/DECISION_LOG.md`, `scanner/scanner.py`, `docs/knowledge/windows_case_only_rename.md` |
| Confidence | HIGH |
| Impact | 511× SMB speed improvement. All future scanning code must comply. |

### D-04: Feature Freeze Policy

| Field | Value |
|---|---|
| Decision | After Milestone close, only Bug Fixes allowed. New features go to next Milestone. |
| Status | **Confirmed** (ADR-003) |
| Evidence | `docs/AI/DECISION_LOG.md`, `AGENTS.md` § Feature Freeze |
| Confidence | HIGH |
| Impact | M8 modules are now frozen. Changes require M9 authorization. |

### D-05: Prefix/Suffix Independent

| Field | Value |
|---|---|
| Decision | Keep `add_prefix` and `add_suffix` as independent RuleStep types. |
| Status | **Confirmed** (ADR-001) |
| Evidence | `docs/AI/DECISION_LOG.md` |
| Confidence | HIGH |
| Impact | Backward compatibility. Migration risk avoided. |

### D-06: Single-level Undo Only

| Field | Value |
|---|---|
| Decision | Maintain single-level Undo. Multi-level deferred. |
| Status | **Confirmed** (ADR-002) |
| Evidence | `docs/AI/DECISION_LOG.md`, `engine/undo_engine.py` |
| Confidence | HIGH |
| Impact | Simple architecture. No undo stack management. |

### D-07: Preview ↔ Rename Share RenamePlan

| Field | Value |
|---|---|
| Decision | Preview and Rename compute targets once via RenamePlanEngine. Both use the same plan. |
| Status | **Confirmed** |
| Evidence | `docs/AI/ARCHITECTURE.md` § Hard Rules, `engine/rename_plan_engine.py` |
| Confidence | HIGH |
| Impact | No drift between preview and actual rename. |

### D-08: Repository = Sole Runtime Source of Truth

| Field | Value |
|---|---|
| Decision | RuleRepository is the single authoritative source. PresetStore is persistence-only. Settings stores metadata only. |
| Status | **Confirmed** |
| Evidence | `AGENTS.md` § Rule Presets § 架构约束, `storage/repository.py` |
| Confidence | HIGH |
| Impact | No state duplication. Clear data ownership. |

### D-09: RuleAnalysis Declares Context Dependencies

| Field | Value |
|---|---|
| Decision | RuleAnalysis runs outside Preview loop. PreviewEngine constructs context on demand. |
| Status | **Confirmed** |
| Evidence | `engine/rule_analysis.py`, `engine/preview_engine.py`, `docs/AI/ARCHITECTURE.md` § Rule Dependency Analysis |
| Confidence | HIGH |
| Impact | Efficient context construction. No unnecessary MetadataProvider calls. |

### D-10: One Milestone, One Core Feature

| Field | Value |
|---|---|
| Decision | Each Milestone introduces exactly one core capability. |
| Status | **Confirmed** |
| Evidence | `AGENTS.md` § One Milestone, One Core Feature |
| Confidence | HIGH |
| Impact | Bounded scope, clear baselines, low regression risk. |

---

## Product Decisions

### D-11: zh_CN as Default Locale

| Field | Value |
|---|---|
| Decision | Application UI defaults to Chinese (zh_CN). English (en_US) available. |
| Status | **Confirmed** |
| Evidence | `i18n/translator.py:12` (`default_lang="zh_CN"`), `translations/zh_CN.ts`, `translations/en_US.ts` |
| Confidence | HIGH |
| Impact | All UI labels in Chinese. i18n infrastructure supports additional languages. |

### D-12: PySide6 over PyQt

| Field | Value |
|---|---|
| Decision | PySide6 (Qt for Python, LGPL) chosen over PyQt6. |
| Status | **Confirmed** |
| Evidence | `requirements.txt` (`PySide6>=6.8`), all UI imports |
| Confidence | HIGH |
| Impact | LGPL licensing. Qt 6 API. |

### D-13: Non-Recursive Scan

| Field | Value |
|---|---|
| Decision | Scanner only scans immediate children. No recursive descent. |
| Status | **Confirmed** |
| Evidence | `scanner/scanner.py` (uses `os.scandir()` in flat mode), `docs/AI/ARCHITECTURE.md` § Scanner |
| Confidence | HIGH |
| Impact | Simple scan model. Directory rename does not affect contents. |

### D-14: JSON Serialization (No Migration Versioning Beyond v1)

| Field | Value |
|---|---|
| Decision | Rules stored as JSON with `version: 1` field. No migration framework. |
| Status | **Confirmed** |
| Evidence | `config/rules.json`, `docs/AI/KNOWN_LIMITATIONS.md` § Serialization |
| Confidence | HIGH |
| Impact | Backward compatibility depends on careful parameter design. |

### D-15: Windows Case-Only Rename via samefile()

| Field | Value |
|---|---|
| Decision | Case-only rename detection uses `Path.samefile()` to compare filesystem identity. |
| Status | **Confirmed** |
| Evidence | `engine/rename_plan_engine.py`, `docs/knowledge/windows_case_only_rename.md` |
| Confidence | HIGH |
| Impact | Correct case-only rename on Windows where `Path.exists()` is case-insensitive. |

### D-16: PresetStore Path

| Field | Value |
|---|---|
| Decision | Presets stored at `~/.resourcehub/presets.json`. Directory auto-created. |
| Status | **Confirmed** |
| Evidence | `storage/preset_store.py`, `docs/AI/M8_COMPLETION.md` |
| Confidence | HIGH |
| Impact | User-level persistence. Separated from application config. |

### D-17: Preset Load Uses deepcopy

| Field | Value |
|---|---|
| Decision | Loading presets from PresetStore applies `deepcopy` to prevent mutation of stored data. |
| Status | **Confirmed** |
| Evidence | `ui/preset_manager_dialog.py`, `docs/AI/M8_COMPLETION.md` |
| Confidence | HIGH |
| Impact | Mutation isolation. Stored presets cannot be corrupted by runtime edits. |

### D-18: Startup Preset Restoration is Defensive

| Field | Value |
|---|---|
| Decision | Missing preset or non-string Settings → silent skip. No error dialog. |
| Status | **Confirmed** |
| Evidence | `ui/main_window.py:_restore_last_preset()`, `docs/AI/M8_COMPLETION.md` |
| Confidence | HIGH |
| Impact | Graceful degradation. No startup errors from stale settings. |

---

## Unconfirmed / Open Decisions

### UD-01: Product Rename to "Rule IDE"

| Field | Value |
|---|---|
| Decision | Has the project been approved to rename from ResourceHub to "Rule IDE"? |
| Status | **Unconfirmed** |
| Evidence | `editor/__init__.py` references "Rule IDE editing layer". `AI_HANDOFF.md` references "M12 Rule IDE". No formal rename document exists. No code references "Rule IDE" as product name. Window title still "ResourceHub v0.1". |
| Confidence | LOW (insufficient evidence for a product rename decision) |
| Impact | If true: all docs, config, build scripts need rename. If false: `editor/` package terminology needs clarification. |

### UD-02: M12 is Number Rule OR Rule IDE

| Field | Value |
|---|---|
| Decision | Is M12 the Number Rule milestone (tagged) or the Rule IDE milestone (planned in AI_HANDOFF.md)? |
| Status | **Unconfirmed** |
| Evidence | `M12-complete` tag = Number Rule. `AI_HANDOFF.md` = "Prepare M12 Rule IDE". These conflict. |
| Confidence | LOW (contradictory evidence) |
| Impact | Milestone numbering confusion for M9 planning. |

### UD-03: Master Design Document Status

| Field | Value |
|---|---|
| Decision | Where is the "Master Design" document referenced by `editor/` package? |
| Status | **Unconfirmed** |
| Evidence | 3 `editor/` source files reference specific sections. Document not in repository. |
| Confidence | HIGH (that it's missing) / LOW (what it contains) |
| Impact | Critical for Rule IDE subsystem understanding. |

---

## Decision Summary

| Category | Count |
|---|---|
| Confirmed Architecture Decisions | 10 |
| Confirmed Product Decisions | 8 |
| Unconfirmed / Open | 3 |
| **Total** | **21** |

---

**Confidence**: HIGH for confirmed decisions (documented in ADRs or authoritative source files). LOW for unconfirmed (insufficient or contradictory evidence).
