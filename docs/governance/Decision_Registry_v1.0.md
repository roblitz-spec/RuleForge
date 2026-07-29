# Decision Registry v1.0

**PAC-1 | Date: 2026-07-24 | Source: `docs/PAC/05_Decision_Registry.md`, `docs/PAC/14_Alignment_Review.md` §7**

---

## Confirmed Decisions

### Architecture Decisions (10)

| # | Decision | ADR | Milestone |
|---|---|---|---|
| D-01 | RuleEngine pure function contract | ADR-004 | M12 |
| D-02 | Context Contract frozen (index, count, metadata) | ADR-005 | M14 |
| D-03 | Avoid Path.resolve() in Scanner (511× SMB speed) | ADR-006 | M11.2 |
| D-04 | Feature Freeze Policy | ADR-003 | M15 RC |
| D-05 | Prefix/Suffix independent RuleStep types | ADR-001 | M15 |
| D-06 | Single-level Undo only | ADR-002 | M15 |
| D-07 | Preview ↔ Rename share RenamePlan | — | — |
| D-08 | Repository = sole Runtime Source of Truth | — | — |
| D-09 | RuleAnalysis declares context dependencies | — | — |
| D-10 | One Milestone, One Core Feature | — | — |

### Product Decisions (8)

| # | Decision | Evidence |
|---|---|---|
| D-11 | zh_CN as default UI locale | `i18n/translator.py:12` |
| D-12 | PySide6 over PyQt6 | `requirements.txt` |
| D-13 | Non-recursive scan (immediate children only) | `scanner/scanner.py` |
| D-14 | JSON serialization with `version: 1`; no migration framework | `config/rules.json` |
| D-15 | Windows case-only rename via `Path.samefile()` | `engine/rename_plan_engine.py` |
| D-16 | PresetStore at `~/.resourcehub/presets.json` | `storage/preset_store.py` |
| D-17 | Preset load uses `deepcopy` for mutation isolation | `ui/preset_manager_dialog.py` |
| D-18 | Startup preset restoration is defensive (silent skip on error) | `ui/main_window.py` |

---

## Unconfirmed / Open Decisions (3)

| # | Question | Status |
|---|---|---|
| UD-01 | Product rename from "ResourceHub" to "Rule IDE"? | **Unconfirmed** — no formal rename evidence |
| UD-02 | M12 = Number Rule (tagged) OR Rule IDE (planned)? | **Unconfirmed** — contradictory evidence |
| UD-03 | Master Design document location? | **Unconfirmed** — referenced by `editor/` but not in repo |

---

## Missing ADRs

Two architectural decisions lack formal ADRs:

| # | Decision | Source Evidence |
|---|---|---|
| ADR-007 | Editor Layer Separation — UI-independent rule editing via `editor/` package (EditSession, DomainValidator) | `editor/` (382 lines) |
| ADR-008 | Preset Architecture — Repository as runtime truth, PresetStore as persistence, Settings as metadata | `AGENTS.md` § Rule Presets, `storage/` (347 lines) |

---

**Source evidence**: `docs/PAC/05_Decision_Registry.md`, `docs/AI/DECISION_LOG.md`, `docs/PAC/14_Alignment_Review.md` §7.
