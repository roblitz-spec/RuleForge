# M8 — Rule Presets: Completion Record

**Date**: 2026-07-24
**Baseline Tag**: `M8-complete`
**Branch**: `m10-phase3a-rule-analysis`
**Previous Baseline**: `M7-complete` (398 tests)

---

## 1. Scope Summary

M8 introduces **Rule Presets** — the ability to save, load, manage, and restore complete Rule configurations as named presets. This enables users to switch between different renaming workflows without manually recreating rule sets.

## 2. Work Packages

| WP | Title | Status | Tests Added | Commit |
|---|---|---|---|---|
| WP-22 | Preset Data Model & Storage | **ACCEPTED** | +22 | `baabcd0` |
| WP-23 | Preset Manager UI | **ACCEPTED** | +9 | `382e756` |
| WP-24 | Toolbar Preset Selector | **ACCEPTED** | +10 | `573b070` |
| WP-25 | Startup Preset Restoration | **ACCEPTED** | +8 | `6f36acc` |
| WP-26 | Documentation & Baseline Freeze | **COMPLETED** | 0 | (this commit) |

## 3. New Modules

| Module | Purpose |
|---|---|
| `models/preset.py` | `Preset` dataclass (id, name, description, rules, version) |
| `storage/preset_store.py` | `PresetStore` — JSON persistence at `~/.resourcehub/presets.json` |
| `ui/preset_manager_dialog.py` | `PresetManagerDialog` — QDialog for save/load/delete/rename |
| `tests/test_preset.py` | 22 PresetStore unit tests |
| `tests/test_preset_workflow.py` | 9 Repository↔PresetStore integration tests |
| `tests/test_preset_toolbar.py` | 10 Toolbar selector integration tests |
| `tests/test_preset_startup.py` | 8 Startup restoration tests |

## 4. Modified Modules

| Module | Changes |
|---|---|
| `storage/repository.py` | `+replace_rules()` public method |
| `config/settings.py` | `+get_last_preset_id()` / `+set_last_preset_id()` |
| `ui/main_window.py` | PresetStore init, preset toolbar row, 4 handler methods, startup restoration |

## 5. Test Results

| Metric | Count |
|---|---|
| Total tests (M8-complete) | **447 PASS** |
| M7 baseline | 398 |
| New in M8 | +49 |
| Regression | 100% PASS |

### Test Breakdown by WP

```
WP-22: test_preset.py           22 tests — CRUD, edge cases, isolation
WP-23: test_preset_workflow.py   9 tests — replace_rules flow, dirty guard
WP-24: test_preset_toolbar.py   10 tests — combo population, preset switching
WP-25: test_preset_startup.py    8 tests — restore, missing, persistence
```

## 6. Architecture Compliance

| Invariant | Status |
|---|---|
| Repository = sole Runtime Source of Truth | ✅ |
| PresetStore = persistent storage only | ✅ |
| Settings = metadata only | ✅ |
| RuleEngine = pure function, stateless | ✅ |
| Context Contract frozen (`index`, `count`, `metadata`) | ✅ |
| No new runtime state sources | ✅ |
| Backward Compatible | ✅ (rules.json unchanged) |
| All public API through Repository | ✅ |
| Deep copy on load (mutation isolation) | ✅ |
| No WP-22/WP-23/WP-24 regressions | ✅ |

## 7. M8 Planning Observations Resolution

| # | Observation | Resolution |
|---|---|---|
| OBS-1 | `replace_rules` naming → consider alternatives | ACCEPTED — `replace_rules` chosen; clear semantics, Repository public API |
| OBS-2 | PresetStore path → validate in WP-22 | RESOLVED — `Path.home() / ".resourcehub" / "presets.json"`, directory auto-created |
| OBS-3 | Dirty session guard → verify in WP-24 | RESOLVED — Guard implemented in WP-23 (PresetManagerDialog); toolbar blocked by modal dialog |
| OBS-4 | Lock-in behavior → document | RESOLVED — No lock-in; preset is one-way load, no bidirectional sync |

## 8. File Diff (M7-complete → M8-complete)

```
 config/settings.py            |   8 +++
 models/preset.py              |  16 +++
 storage/preset_store.py       | 129 +++++++++++++++++++++
 storage/repository.py         |   4 +
 tests/test_preset.py          | 264 +++++++++++++++++++++++++++++++++++++
 tests/test_preset_startup.py  | 164 ++++++++++++++++++++++++
 tests/test_preset_toolbar.py  | 185 +++++++++++++++++++++++++++
 tests/test_preset_workflow.py | 237 +++++++++++++++++++++++++++++++++
 ui/main_window.py             | 109 +++++++++++++++++-
 ui/preset_manager_dialog.py   | 216 ++++++++++++++++++++++++++++++
 10 files changed, 1331 insertions(+), 1 deletion(-)
```

## 9. Architecture Notes

- `Preset` is a pure data object (dataclass) — no behavior, no validation
- `PresetStore` has no knowledge of `Repository` — decoupled through `replace_rules()`
- Toolbar combo maps display names to preset IDs via QComboBox user data
- Startup restoration is defensive: missing preset → silent skip, non-string Settings → None
- All preset loading uses `deepcopy` to prevent mutation of stored presets

## 10. Known Limitations

| Limitation | Note |
|---|---|
| No bidirectional sync | Modifying rules after loading a preset does not update the preset; must re-save manually |
| No merge/partial load | `replace_rules` replaces all rules atomically; no selective rule loading |
| No import/export | Presets share the same `presets.json`; no file import/export UI |
| No preset description editing in toolbar | Description editing requires PresetManagerDialog |

---

**M8 Complete.** Frozen at `M8-complete`.
