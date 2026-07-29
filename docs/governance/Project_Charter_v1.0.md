# Project Charter v1.0

**PAC-1 | Date: 2026-07-24 | Source: `docs/PAC/14_Alignment_Review.md` §2, §11**

---

## Project Identity

| Attribute | Value |
|---|---|
| **Project Name** | ResourceHub |
| **Type** | Windows desktop application |
| **Purpose** | Batch file rename tool with rule-based transformations, preview, and undo |
| **Current Version** | M8 (M8-complete) |
| **Window Title** | ResourceHub v0.1 |
| **Repository** | `/projects/ResourceHub` |

---

## Core Capabilities

- **10 RuleStep types**: replace, remove_text, regex_replace, case, trim, number, insert, date, add_prefix, add_suffix
- **Pipeline**: Scanner → PreviewEngine → RenamePlanEngine → RenameEngine → UndoEngine
- **Rule Presets**: Save/load/delete/rename via PresetManagerDialog
- **Rule Editor**: EditSession with DomainValidator for UI-independent rule editing
- **UI**: PySide6 (Qt 6), Chinese (zh_CN) default locale, English (en_US) available
- **Tests**: 447 automated tests, all passing
- **Platform**: Windows desktop exe via PyInstaller

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| GUI Framework | PySide6 (Qt 6, LGPL) |
| Storage | JSON (`rules.json`, `~/.resourcehub/presets.json`) |
| Settings | QSettings |
| Packaging | PyInstaller (single exe) |
| Testing | pytest |

---

## Governance

The project is governed by the AI Workflow SOP (`docs/AI/AI_WORKFLOW.md`) and Development Constitution (`docs/AI/DEVELOPMENT_CONSTITUTION.md`).

Key governance principles:
- One Milestone, One Core Feature
- Feature Freeze after Milestone close
- Backward compatibility required
- Evidence-based decision making

All governance artifacts are in `docs/governance/` and `docs/AI/`.

---

## Charter Completeness

This charter is based on PAC-1 discovery evidence. The following items are **not yet defined** and require governance resolution:

| Item | Status | Reference |
|---|---|---|
| Rule IDE scope and definition | Pending | PG-01 |
| Stakeholder identification | Not documented | — |
| Success criteria / v1.0 definition | Not documented | PG-05 |
| Non-goals / scope boundaries | Not documented | — |
| Decision authority structure | Not documented | — |

---

**Source evidence**: `docs/PAC/01_Project_Identity.md`, `docs/PAC/02_Product_Evolution.md`, `docs/PAC/14_Alignment_Review.md`.
