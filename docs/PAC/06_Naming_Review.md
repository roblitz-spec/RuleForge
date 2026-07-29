# 06 — Naming Review

**PAC-1 Discovery | Date: 2026-07-24**

This document **does not recommend** a name. It inventories historical and working names with evaluation criteria.

---

## 1. Historical Names

### ResourceHub (Confirmed)

| Attribute | Evidence |
|---|---|
| First usage | Earliest commits in git history |
| All documentation | 12 `docs/AI/` documents begin with "# ResourceHub —" |
| Source code | `main_window.py`: `"ResourceHub v0.1"` |
| Configuration | `config/settings.py`: `_ORGANIZATION = "ResourceHub"`, `_APPLICATION = "ResourceHub"` |
| Build artifact | `build.spec`: EXE name = `"ResourceHub"` |
| README | `README.md`: "# ResourceHub" |
| AGENTS.md | `AGENTS.md`: "# ResourceHub — 开发参考" |
| Git configuration | Repository root is `/projects/ResourceHub` |

**Status**: The only project name in active use. No rename has occurred.

**Confidence**: HIGH

---

## 2. Working Names

### "Rule IDE" (Evolving, Not Adopted)

| Attribute | Evidence |
|---|---|
| Source | `editor/__init__.py`: `# Editor Core — Rule IDE editing layer (Master Design, Section 3)` |
| Planning reference | `docs/AI/AI_HANDOFF.md`: `"4. Prepare M12 Rule IDE"` |
| Technical debt triggers | `docs/AI/CURRENT_STATUS.md` TD-003, TD-018 |
| Implementation | `editor/` package (382 lines) — actively used |
| Product rename | **Not executed** — no window title change, no config change, no doc rename |

**Status**: "Rule IDE" describes a subsystem/architectural layer, not a product. The `editor/` package uses it as a code-level descriptor. `AI_HANDOFF.md` uses it as a milestone name.

**Confidence**: MEDIUM (code references exist; product rename evidence is absent)

---

## 3. Reasons for Changes

**No name change has occurred.** ResourceHub is the only name in repository history.

Evidence (HIGH):
- `git log --all` shows 0 commits renaming the project
- `grep -r "Rule IDE"` returns only `editor/` docstrings + `AI_HANDOFF.md` + `CURRENT_STATUS.md` — no product-level rename
- All documentation headers use "ResourceHub"

---

## 4. Repository Evidence Summary

| Name | Type | Evidence Count | Locations |
|---|---|---|---|
| ResourceHub | Product name | 30+ | README, all docs/AI/, config, build, window title, AGENTS.md |
| Rule IDE | Subsystem/planning reference | 5 | editor/ (x3), AI_HANDOFF.md, CURRENT_STATUS.md |
| RULEHUB | None found | 0 | — |
| RenamePro | None found | 0 | — |
| Any other candidate | None found | 0 | — |

---

## 5. Candidate Names Discussed

**Only two names appear in repository:**

| Candidate | Type | First Evidence |
|---|---|---|
| **ResourceHub** | Current product name | Repository creation |
| **Rule IDE** | Subsystem descriptor / planned milestone name | `editor/` package + `AI_HANDOFF.md` |

---

## 6. Evaluation (Criteria from PAC-1 Specification)

### ResourceHub

| Criterion | Assessment | Rationale |
|---|---|---|
| Domain Accuracy | **Low** | "Hub" implies aggregation/collection. The product is a rename tool + rule editor, not a resource hub. |
| Scalability | **Medium** | "Hub" could encompass future features (filter, EXIF, variables), but doesn't signal the rule-centric direction. |
| User Expectations | **Medium** | Name doesn't clearly communicate "rename tool" or "rule editor." Users must read description. |
| Technical Accuracy | **Low** | No "resource" concept in the codebase. Core domain objects are Rule, FileItem, Preset. |
| Brand Flexibility | **High** | Single word, unique, no trademark conflicts apparent. Memorable. |

### Rule IDE

| Criterion | Assessment | Rationale |
|---|---|---|
| Domain Accuracy | **High** | "Rule" + "IDE" accurately describes the current direction — rule editing, validation, session management. |
| Scalability | **High** | IDE concept naturally encompasses filter, EXIF, variables as features within the editing environment. |
| User Expectations | **Medium** | "IDE" implies developer tool; may overshoot for batch rename users. |
| Technical Accuracy | **High** | Editor package, DomainValidator, EditSession — IDE infrastructure already exists. |
| Brand Flexibility | **Medium** | "Rule IDE" is descriptive but generic. Harder to trademark. |

---

## 7. Naming Assessment

| Question | Answer |
|---|---|
| Has the project been renamed? | **No.** ResourceHub is the only name. |
| Is a rename planned? | **Unclear.** `AI_HANDOFF.md` references "M12 Rule IDE" but this conflicts with existing `M12-complete` (Number Rule). |
| Is "Rule IDE" a product name or subsystem? | **Subsystem.** The `editor/` package uses it as a code-layer descriptor. No product-level rename evidence. |
| Are there other candidate names? | **None found.** Only ResourceHub and Rule IDE appear. |

---

**Confidence**:
- Historical names: HIGH (git history is unambiguous)
- Working names: MEDIUM (Rule IDE appears but has no product-level adoption)
- Reasons for changes: N/A (no changes occurred)
- Candidate names discussed: HIGH (only 2 names found via exhaustive search)
