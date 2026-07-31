# 01 — Project Identity Discovery

**PAC-1 Discovery | Date: 2026-07-24 | Confidence: HIGH**

---

## 1. Original Project Purpose

**Confirmed**: ResourceHub is a Windows desktop batch file rename tool.

**Evidence**:
- `README.md` (line 1): "# ResourceHub — Windows 桌面批量重命名工具。"
- `docs/AI/PROJECT_BRIEF.md`: "ResourceHub is a Windows desktop batch file rename tool built with Python 3.12+ and PySide6."
- `docs/AI/AI_MEMORY_PACK.md`: "ResourceHub is a Windows desktop batch file rename tool."
- `build.spec`: EXE name = "ResourceHub"

**Confidence**: HIGH (4 independent sources)

---

## 2. Current Project Purpose

**Confirmed**: ResourceHub remains a batch file rename tool. The purpose has not been formally redefined in any repository document.

**Evidence**:
- `docs/AI/PROJECT_BRIEF.md` has not been updated to reflect any purpose change.
- `README.md` has not been updated (16 lines, unchanged from creation).
- Window title at runtime: `"ResourceHub v0.1"` (`ui/main_window.py:85`).

**Inferred**: The project has added a Rule IDE subsystem (`editor/` package), but this is an infrastructure expansion, not a purpose redefinition.

**Confidence**: HIGH (purpose unchanged in documentation)

---

## 3. Current Core Domain

**Confirmed**: Batch file rename with rule-based transformations.

**Evidence**:
- Pipeline: `Scanner → PreviewEngine → RenamePlanEngine → RenameEngine → UndoEngine` (`docs/AI/ARCHITECTURE.md`)
- 10 RuleStep types: replace, remove_text, regex_replace, case, trim, number, insert, date, add_prefix, add_suffix (`AGENTS.md`)
- `config/rules.json`: Rule configuration as the primary domain object

**Inferred**: The domain is expanding toward a "Rule IDE" — a dedicated rule editing and management environment — as evidenced by the `editor/` package and `AI_HANDOFF.md` references.

**Confidence**: HIGH (confirmed) / MEDIUM (inferred expansion)

---

## 4. Current Primary Asset

**Confirmed**: The Rule configuration (`rules.json`) and the Rule editing pipeline.

**Evidence**:
- All tests are organized around Rule behavior (rule_engine, rule_editor, rule_analysis, rule_step).
- `config/rules.json` is the primary persisted domain object.
- `RuleRepository` is the single authoritative data access layer (`AGENTS.md` § 架构原则).
- `Rule` is the central domain model (`models/rule.py`).

**Confidence**: HIGH

---

## 5. Current Primary User

**Inferred**: Desktop users performing batch file rename operations, with configuration managed through a GUI.

**Evidence**:
- PySide6 GUI (`QMainWindow`, `QTableView`, `QComboBox`, `QDialog`).
- i18n support: zh_CN (default), en_US (`translations/zh_CN.ts`, `en_US.ts`).
- PyInstaller packaging for desktop distribution (`build.spec`, `scripts/build.py`).
- Window title: "ResourceHub v0.1".

**Unknown**: No user research, persona documents, or usage analytics in the repository. Primary user profile is inferred from technology choices and localization defaults.

**Confidence**: MEDIUM (inferred from implementation; no user research docs)

---

## 6. Separating Confirmed / Inferred / Unknown

| Category | Item | Confidence |
|---|---|---|
| Confirmed | Project name is "ResourceHub" | HIGH |
| Confirmed | Batch file rename tool | HIGH |
| Confirmed | Python 3.12+ / PySide6 | HIGH |
| Confirmed | 10 RuleStep types | HIGH |
| Confirmed | Desktop application (GUI) | HIGH |
| Confirmed | Primary domain object: Rule | HIGH |
| Confirmed | zh_CN default locale | HIGH |
| Inferred | Primary user: Windows desktop user | MEDIUM |
| Inferred | Expanding toward Rule IDE | MEDIUM |
| Unknown | User personas | — |
| Unknown | Target market size | — |
| Unknown | Release timeline to 1.0 | — |
