# 07 — Open Questions

**PAC-1 Discovery | Date: 2026-07-24**

These are unresolved questions requiring governance attention. They will become PAC-1 review topics.

---

## Q-01: What Is the Project Called?

| Field | Value |
|---|---|
| Question | Is the product "ResourceHub" or "ResourceHub — RULE IDE" or something else? |
| Why it matters | Project identity affects documentation, build artifacts, user expectations, and milestone naming. |
| Evidence available | ResourceHub: 30+ references across all docs, config, window title. Rule IDE: 5 references (editor/ package + planning docs). |
| Evidence missing | No formal naming decision. No project charter. No rename commit. |

**Impact**: All governance docs, build config, and UI labels depend on this answer.

---

## Q-02: Where Is the "Master Design" Document?

| Field | Value |
|---|---|
| Question | The `editor/` package references a "Master Design" document with specific sections (Section 3, AD-03, Section 4.1). Where is it? |
| Why it matters | 382 lines of production code reference a design that can't be reviewed. New contributors to the Rule IDE subsystem cannot understand the design rationale. |
| Evidence available | 3 `editor/` module docstrings with specific section references. All 26 repository documents searched — no match. |
| Evidence missing | Document contents, author, creation date, location (external?). |

**Impact**: Blocks understanding of Rule IDE architecture intent.

---

## Q-03: What Is M12?

| Field | Value |
|---|---|
| Question | M12 is tagged as "Number Rule" (M12-complete). But `AI_HANDOFF.md` says "Prepare M12 Rule IDE." Which is M12? |
| Why it matters | Milestone numbering confusion. M9 planning needs to know what numbers are available. |
| Evidence available | `M12-complete` tag = Number Rule. `AI_HANDOFF.md:23` = "M12 Rule IDE." |
| Evidence missing | Any document reconciling these two M12 definitions. |

**Impact**: M9 planning may accidentally collide with existing M12 if numbering isn't clarified.

---

## Q-04: What Happened to M9, M10, M11.1?

| Field | Value |
|---|---|
| Question | Tags jump from M8 to M11.2 to M12. Where are M9, M10, M11.1? |
| Why it matters | Incomplete milestone history. Were these skipped, merged into the current branch, or completed without tags? |
| Evidence available | Branch `m10-phase3a-rule-analysis` suggests M10 had work. `docs/development/current_status.md` references M10 Phase 3A (RuleAnalysis). M11.1 has a scanner module reference but no tag. |
| Evidence missing | M9 scope, M10 deliverables, M11.1 completion status. |

**Impact**: Gaps in project history. Cannot reconstruct full development timeline.

---

## Q-05: Is M9 the Filter System or Rule IDE?

| Field | Value |
|---|---|
| Question | `NEXT_MILESTONE.md` ranks Filter System as P1. `AI_HANDOFF.md` references Rule IDE as the next direction. Which is M9? |
| Why it matters | M8 is closed. The next milestone needs a clear scope before development begins. |
| Evidence available | `NEXT_MILESTONE.md`: Filter=P1, EXIF=P2, Variables=P4. `AI_HANDOFF.md`: "Prepare M12 Rule IDE" (stale). |
| Evidence missing | M9 scope decision. Prioritization rationale for Filter vs. Rule IDE. |

**Impact**: M9 cannot start until scope is decided.

---

## Q-06: Should the Project Have a Versioning Policy?

| Field | Value |
|---|---|
| Question | Window title says "v0.1." Is there a plan for v1.0? What are the release criteria? |
| Why it matters | Users and contributors need to know what "1.0" means and when to expect it. |
| Evidence available | Window title (`ui/main_window.py:85`): "ResourceHub v0.1". No versioning document. No release checklist. No changelog for end-users. |
| Evidence missing | Version scheme (semver? calver?), release criteria, release cadence. |

**Impact**: Unclear when ResourceHub should be considered "released."

---

## Q-07: What Is the Target User Profile?

| Field | Value |
|---|---|
| Question | Who is this application for? Photographers (EXIF date)? Developers (regex)? General Windows users? |
| Why it matters | Feature prioritization (Filter vs. EXIF vs. Variables) depends on user needs. |
| Evidence available | zh_CN default locale (Chinese users). Windows-only (PySide6). Batch rename + undo (safety-conscious). |
| Evidence missing | User personas, usage data, feature requests, market research. |

**Impact**: Feature prioritization is based on developer intuition, not user data.

---

## Q-08: Is There an Intended Release Timeline?

| Field | Value |
|---|---|
| Question | When should ResourceHub reach v1.0? Is there a target date or milestone count? |
| Why it matters | Planning horizon. Resource allocation. Feature freeze decisions. |
| Evidence available | Milestone-based development. No time-bound planning. No release date mentioned anywhere. |
| Evidence missing | Target date, release milestones, go/no-go criteria. |

**Impact**: Development continues indefinitely with no release pressure or deadline.

---

## Q-09: Should `add_suffix` Be Added to AGENTS.md?

| Field | Value |
|---|---|
| Question | M15 delivered `add_suffix` RuleStep. AGENTS.md vstable still shows only 9 types. Should it be added? |
| Why it matters | AGENTS.md is the authoritative RuleStep reference. Missing entries cause confusion. |
| Evidence available | M15-complete tag. `add_suffix` handler exists in `engine/rule_engine.py`. Not in AGENTS.md table. |
| Evidence missing | None — this is a straightforward documentation gap. |

**Impact**: LOW (documentation only). But every new AI session reads AGENTS.md as reference.

---

## Question Summary

| ID | Topic | Priority | Blocking M9? |
|---|---|---|---|
| Q-01 | Project name | HIGH | No (but should be resolved) |
| Q-02 | Master Design document | HIGH | No (but needed for Rule IDE work) |
| Q-03 | M12 definition conflict | MEDIUM | Yes (numbering confusion) |
| Q-04 | M9/M10/M11.1 gaps | MEDIUM | Yes (history clarity) |
| Q-05 | M9 scope (Filter vs. Rule IDE) | HIGH | **Yes** |
| Q-06 | Versioning policy | LOW | No |
| Q-07 | User profile | MEDIUM | No (but affects prioritization) |
| Q-08 | Release timeline | LOW | No |
| Q-09 | AGENTS.md add_suffix gap | LOW | No |

---

**Confidence**: HIGH for question identification (all gaps confirmed by repository search). LOW for answers (insufficient evidence for all questions).
