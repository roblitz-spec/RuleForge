# 09 — Evidence Cross Validation

**PAC-1 Phase 2 | Date: 2026-07-24**

Every conflict is evidence-based. This document does NOT determine which artifact is correct.

---

## Conflict Inventory

### C-01: AGENTS.md RuleStep Table Missing `add_suffix`

| Field | Value |
|---|---|
| Artifact A | `AGENTS.md` § RuleStep 类型总览 — lists 9 types |
| Artifact B | `engine/rule_engine.py` — defines 10 `_handle_*` functions + 10 `_HANDLERS` entries |
| Conflict | AGENTS.md table shows 9 types; code has 10. `add_suffix` is missing from AGENTS.md. |
| Possible Cause | M15 added `add_suffix`. AGENTS.md was updated for M6/M7/M8 baselines but the RuleStep table was not updated for M15 (earlier branch). |
| Confidence | **HIGH** |

---

### C-02: NEXT_MILESTONE.md Lists Rule Presets as P3 (Already Completed)

| Field | Value |
|---|---|
| Artifact A | `docs/AI/NEXT_MILESTONE.md` — "P3 \| Rule Presets \| Save/load complete rule pipelines" |
| Artifact B | `docs/AI/CURRENT_STATUS.md` — "M8 Rule Presets — Complete ✅"; `M8-complete` tag exists |
| Conflict | NEXT_MILESTONE.md still lists Rule Presets as P3 planned work. M8 completed it (447 tests, `M8-complete` tag). |
| Possible Cause | NEXT_MILESTONE.md was not updated after M8 closure. Per `README_AI.md`, NEXT_MILESTONE.md should be updated "Every Milestone". |
| Confidence | **HIGH** |

---

### C-03: Multiple Docs Claim M11.2; Active Baseline Is M8

| Field | Value |
|---|---|
| Artifact A | `docs/AI/PROJECT_BRIEF.md` — "Current Version: M11.2" |
| Artifact B | `docs/AI/AI_HANDOFF.md` — "Milestone: M11.2", "Status: Stabilization" |
| Artifact C | `docs/AI/AI_MEMORY_PACK.md` — "Version: M11.1" |
| Artifact D | `docs/development/current_status.md` — "M11.2 — UX Improvement & Stability Fixes" |
| Artifact E | `docs/AI/CURRENT_STATUS.md` — "Active Baseline: M8 (M8-complete)" |
| Artifact F | `ui/main_window.py:85` — `"ResourceHub v0.1"` |
| Conflict | Four documents claim M11.2/M11.1 as current. CURRENT_STATUS.md says M8. Window title says v0.1. No document aligns. |
| Possible Cause | M11.2 was a previous baseline on a different branch (`m10-phase3a-rule-analysis`). M2–M8 are newer baselines on the same branch. Documentation was not synchronized. |
| Confidence | **HIGH** |

---

### C-04: AI_HANDOFF.md Says "Stabilization"; M8 Is Complete

| Field | Value |
|---|---|
| Artifact A | `docs/AI/AI_HANDOFF.md` — "Status: Stabilization" |
| Artifact B | `docs/AI/CURRENT_STATUS.md` — "M8 Rule Presets — Complete ✅"; `M8-complete` tag; clean working tree; 447 tests |
| Conflict | AI_HANDOFF claims the project is in "Stabilization" for M11.2. The actual state is M8 complete and frozen. |
| Possible Cause | AI_HANDOFF.md not updated since M8 completion. Per `README_AI.md`, it should be updated "Every Milestone". |
| Confidence | **HIGH** |

---

### C-05: AI_HANDOFF.md References "M12 Rule IDE"; Actual M12 Is Number Rule

| Field | Value |
|---|---|
| Artifact A | `docs/AI/AI_HANDOFF.md:23` — "4. Prepare M12 Rule IDE" |
| Artifact B | `git tag -l` — `M12-complete` = Number Rule (122 tests) |
| Conflict | AI_HANDOFF plans for "M12 Rule IDE." Git tag shows M12 was Number Rule. |
| Possible Cause | AI_HANDOFF was written when M12 was planned as Rule IDE. The plan changed (Number Rule was implemented instead), but the document was not updated. |
| Confidence | **HIGH** |

---

### C-06: CHANGELOG_AI.md Has Two "M8" Entries

| Field | Value |
|---|---|
| Artifact A | `docs/AI/CHANGELOG_AI.md` — "## M8 (Rule Presets)" (top entry, 447 tests) |
| Artifact B | `docs/AI/CHANGELOG_AI.md` — "## M8-M11" (bottom entry, "Core Pipeline, RuleEngine v1") |
| Conflict | Two entries claim "M8" — one is the recent Rule Presets milestone, the other is early pipeline work (M8–M11). The bottom entry uses "M8-M11" as a range but the heading format matches a single milestone. |
| Possible Cause | The "M8-M11" entry predates the M2–M8 renumbering. When the new M8 was added, the old entry was not renamed or clarified. |
| Confidence | **HIGH** |

---

### C-07: ARCHITECTURE.md Omits 7 Active Packages

| Field | Value |
|---|---|
| Artifact A | `docs/AI/ARCHITECTURE.md` § Module Boundaries — documents 10 modules (Scanner, RuleEngine, PreviewEngine, RuleAnalysis, RenamePlanEngine, RenameEngine, UndoEngine, FileTableModel, RuleManagerDialog, MainWindow) |
| Artifact B | Repository `ls -d */` — 14 packages: engine/, editor/, validator/, workers/, i18n/, config/, storage/, scanner/, models/, ui/, app/, scripts/, tools/, resources/ |
| Missing | `editor/` (382 lines), `validator/` (75 lines), `workers/` (128 lines), `i18n/` (36 lines), `config/` (48 lines), `storage/` (347 lines), `models/` (dataclasses) |
| Possible Cause | ARCHITECTURE.md was written for the core pipeline. New packages (editor, storage, preset) were added later and the document was not updated. |
| Confidence | **HIGH** |

---

### C-08: ARCHITECTURE.md Missing M8 Modules

| Field | Value |
|---|---|
| Artifact A | `docs/AI/ARCHITECTURE.md` § Module Boundaries — no mention of PresetStore, PresetManagerDialog, or preset-related modules |
| Artifact B | `storage/preset_store.py` (129 lines), `ui/preset_manager_dialog.py` (216 lines), `models/preset.py` (16 lines) — all production code |
| Conflict | ARCHITECTURE.md is the authoritative architecture reference. M8 added significant new modules that are not documented there. |
| Possible Cause | M8 completed but ARCHITECTURE.md was not updated. Per `README_AI.md`, ARCHITECTURE.md should be updated "When pipeline or boundaries change." |
| Confidence | **HIGH** |

---

### C-09: development/current_status.md Stale vs AI/CURRENT_STATUS.md

| Field | Value |
|---|---|
| Artifact A | `docs/development/current_status.md` — "M11.2 — UX Improvement & Stability Fixes", "Pending: Remove temporary debug logging, M12 planning" |
| Artifact B | `docs/AI/CURRENT_STATUS.md` — "M8 (M8-complete)", "447 tests", project status table |
| Conflict | Two "current status" documents describe completely different project states. |
| Possible Cause | `docs/development/current_status.md` is a checkpoint document from earlier work. It was never updated or deleted. `docs/AI/CURRENT_STATUS.md` is the current governance source. |
| Confidence | **HIGH** |

---

### C-10: PROJECT_BRIEF Lists "10 RuleStep Types" But AGENTS.md Shows 9

| Field | Value |
|---|---|
| Artifact A | `docs/AI/PROJECT_BRIEF.md` — "Rule Engine: 10 RuleStep types (replace, remove_text, regex_replace, case, trim, number, insert, date, add_prefix, add_suffix)" |
| Artifact B | `AGENTS.md` § RuleStep 类型总览 — lists 9 types (missing add_suffix) |
| Conflict | PROJECT_BRIEF correctly lists 10 types including add_suffix. AGENTS.md only lists 9. |
| Possible Cause | Same root cause as C-01. AGENTS.md RuleStep table was not updated for M15. |
| Confidence | **HIGH** |

---

### C-11: Window Title "v0.1" vs M8/M11.2 Baselines

| Field | Value |
|---|---|
| Artifact A | `ui/main_window.py:85` — `self.setWindowTitle("ResourceHub v0.1")` |
| Artifact B | `M8-complete` tag (447 tests), `M11.2-complete` tag |
| Conflict | Window title says "v0.1". No document links v0.1 to any milestone. No versioning policy exists. |
| Possible Cause | "v0.1" was set during initial development and never updated. No versioning policy exists to guide updates. |
| Confidence | **HIGH** |

---

### C-12: Empty Packages in Repository

| Field | Value |
|---|---|
| Artifact A | `app/__init__.py` — 0 bytes, no modules |
| Artifact B | `resources/` — empty directory |
| Artifact C | `docs/AI/ARCHITECTURE.md` — no mention of `app/` or `resources/` |
| Conflict | Two empty packages exist in the repository but are never imported, documented, or used. |
| Possible Cause | `app/` and `resources/` may have been created for future use (e.g., Qt resources, application-level logic) but never populated. |
| Confidence | **HIGH** |

---

### C-13: CHANGELOG Missing M2–M5 Entries

| Field | Value |
|---|---|
| Artifact A | `git tag -l` — `M2-complete`, `M3-complete`, `M4-complete`, `M4.1-complete`, `M5-complete` |
| Artifact B | `docs/AI/CHANGELOG_AI.md` — entries start at M5 (indirectly in M6), with earliest direct entry at M8-M11 |
| Conflict | CHANGELOG has explicit entries for M6–M8 and M8–M16, but M2–M5 have no entries. |
| Possible Cause | CHANGELOG was created after M5. M2–M5 were tagged retroactively (see `AGENTS.md` baseline table). |
| Confidence | **HIGH** |

---

### C-14: KNOWN_LIMITATIONS.md Not Updated for M8

| Field | Value |
|---|---|
| Artifact A | `docs/AI/KNOWN_LIMITATIONS.md` — no mention of Rule Presets or preset-related limitations |
| Artifact B | `docs/AI/M8_COMPLETION.md` § Known Limitations — "No bidirectional sync", "No merge/partial load", "No import/export", "No preset description editing in toolbar" |
| Conflict | M8 introduced 4 known limitations. KNOWN_LIMITATIONS.md does not reflect them. |
| Possible Cause | KNOWN_LIMITATIONS.md was not updated after M8. Per `README_AI.md`, it should be updated "When a limitation changes." |
| Confidence | **HIGH** |

---

### C-15: TEST_STRATEGY.md Has No Quantitative Baselines

| Field | Value |
|---|---|
| Artifact A | `docs/AI/TEST_STRATEGY.md` — test layers table, no specific test count |
| Artifact B | `docs/AI/CURRENT_STATUS.md` — 447 tests, detailed WP-level breakdown |
| Conflict | TEST_STRATEGY.md is the authoritative test policy but contains no quantitative baseline. Current test count (447) is only in CURRENT_STATUS.md. |
| Possible Cause | TEST_STRATEGY.md was designed as a policy document, not a status tracker. But lack of any reference to current test counts reduces its value as a release gate document. |
| Confidence | **MEDIUM** |

---

### C-16: DEVELOPMENT_CONSTITUTION.md Missing editor/ in Module Governance

| Field | Value |
|---|---|
| Artifact A | `docs/AI/DEVELOPMENT_CONSTITUTION.md` — "Extension over Modification — New features add handlers, don't change existing ones" |
| Artifact B | `editor/` package — introduces `EditSession` and `DomainValidator` as new modules, not handlers |
| Conflict | Constitution's extension strategy focuses on RuleStep handlers. The `editor/` package represents a different kind of extension (new architectural layer) that isn't covered by the existing principles. |
| Possible Cause | Constitution was written before `editor/` package was introduced. The "extension over modification" principle doesn't address architectural layer additions. |
| Confidence | **MEDIUM** |

---

### C-17: NEXT_MILESTONE.md Not Updated After M8

| Field | Value |
|---|---|
| Artifact A | `docs/AI/NEXT_MILESTONE.md` — still lists Rule Presets (P3), no "Completed" section, no M8 reflection |
| Artifact B | `docs/AI/README_AI.md` Mandatory Update Checklist — "NEXT_MILESTONE.md — plan next" every Milestone |
| Conflict | NEXT_MILESTONE.md should have been updated after M8. It was not. |
| Possible Cause | M8 WP-26 (Documentation & Baseline Freeze) updated CHANGELOG, CURRENT_STATUS, AGENTS.md but missed NEXT_MILESTONE.md. |
| Confidence | **HIGH** |

---

### C-18: README.md Insufficient for Project Maturity

| Field | Value |
|---|---|
| Artifact A | `README.md` — 16 lines: project name, tech stack, run command |
| Artifact B | `docs/AI/PROJECT_BRIEF.md` — 22 lines: capabilities, features, architecture summary |
| Artifact C | `docs/AI/CURRENT_STATUS.md` — 130+ lines: full status, debt register |
| Conflict | README.md is the front door of the project but contains almost no information. All substantive documentation is in `docs/AI/`, invisible to non-AI contributors. |
| Possible Cause | The project's documentation strategy prioritizes AI-consumable docs (`docs/AI/`). README was never expanded. |
| Confidence | **HIGH** |

---

### C-19: AGENTS.md vs CHANGELOG vs CURRENT_STATUS Counting

| Field | Value |
|---|---|
| Artifact A | `AGENTS.md` — M6: 384 tests, M7: 398 tests, M8: 447 tests |
| Artifact B | `CHANGELOG_AI.md` — M6: 384, M7: 398, M8: 447 |
| Artifact C | `CURRENT_STATUS.md` — M7: 398 + WP-22: 22 + WP-23: 9 + WP-24: 10 + WP-25: 8 = 447 |
| Artifact D | Actual `pytest` — 447 passed |
| Assessment | **CONSISTENT** — all test counts align across documents and with reality. This is a positive finding. |
| Confidence | **HIGH (CONSISTENT)** |

---

## Conflict Summary

| ID | Severity | Type | Docs Affected |
|---|---|---|---|
| C-01 | MEDIUM | Missing data | AGENTS.md vs code |
| C-02 | HIGH | Stale planning | NEXT_MILESTONE.md |
| C-03 | HIGH | Version mismatch | PROJECT_BRIEF, AI_HANDOFF, AI_MEMORY_PACK, development/current_status vs CURRENT_STATUS |
| C-04 | HIGH | Stale status | AI_HANDOFF.md |
| C-05 | MEDIUM | Stale planning | AI_HANDOFF.md vs git tag |
| C-06 | LOW | Naming conflict | CHANGELOG_AI.md |
| C-07 | HIGH | Undocumented modules | ARCHITECTURE.md vs 7 packages |
| C-08 | HIGH | Missing M8 modules | ARCHITECTURE.md vs preset code |
| C-09 | MEDIUM | Duplicate doc | development/current_status.md |
| C-10 | MEDIUM | Table inconsistency | AGENTS.md vs PROJECT_BRIEF |
| C-11 | LOW | Stale version | Window title |
| C-12 | LOW | Dead packages | app/, resources/ |
| C-13 | LOW | Missing history | CHANGELOG_AI.md |
| C-14 | MEDIUM | Stale limitations | KNOWN_LIMITATIONS.md |
| C-15 | LOW | No baselines | TEST_STRATEGY.md |
| C-16 | LOW | Principle gap | DEVELOPMENT_CONSTITUTION.md |
| C-17 | MEDIUM | Stale planning | NEXT_MILESTONE.md |
| C-18 | LOW | Incomplete | README.md |
| C-19 | — | ✅ CONSISTENT | AGENTS.md, CHANGELOG, CURRENT_STATUS, pytest |

---

**Confidence**: HIGH for all 18 conflicts (verified by file content comparison + git tag inspection).
