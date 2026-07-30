# RuleForge — AI Changelog

> For architecture decisions behind these changes, see [`DECISION_LOG.md`](DECISION_LOG.md).

## M8 (Rule Presets)
- **WP-22: Preset Data Model & Storage** — `Preset` dataclass + `PresetStore` JSON CRUD
- **WP-23: Preset Manager UI** — `PresetManagerDialog` (save/load/delete/rename) + `Repository.replace_rules()`
- **WP-24: Toolbar Preset Selector** — QComboBox preset switcher in MainWindow toolbar
- **WP-25: Startup Preset Restoration** — `Settings` last-used preset persistence + auto-restore on launch
- **Tests**: 447 PASS (M7: 398 + WP-22: +22 + WP-23: +9 + WP-24: +10 + WP-25: +8)
- **New Modules**: `models/preset.py`, `storage/preset_store.py`, `ui/preset_manager_dialog.py`
- **New Tests**: `tests/test_preset.py`, `tests/test_preset_workflow.py`, `tests/test_preset_toolbar.py`, `tests/test_preset_startup.py`

## M7 (Architecture Consolidation & Quality Hardening)
- **WP-19: ID Generation Consolidation** — `RuleRepository.generate_unique_id()` as single ID authority, removed duplicate from dialog
- **WP-20: EditSession Interaction Coverage** — 10 tests covering EditSession × duplicate boundary
- **Tests**: 398 PASS (M6: 384 + WP-19: +4 + WP-20: +10)

## M6 (Rule Duplication)
- **Rule Duplication**: `RuleRepository.duplicate()` — deep copy with unique ID, `(副本)` name suffix, unpinned
- **UI Integration**: "复制规则" context menu action in rule manager dialog
- **Review**: Independent review approved with 6 non-blocking observations (see `REVIEW_M6.md`)
- **Tests**: 384 PASS (M5: 356 + M6: +28)

## M11.2
- **Sortable Table**: Column header click sorting, context menu (copy/paste)
- **Pin Rules**: Rule pinning for quick access in rule list
- **Regex Assistant**: Built-in regex templates (filename cleanup, content extraction, advanced)
- **NAS Performance Fix**: Removed `Path.resolve()` from Scanner hot path, 511× SMB speedup
- **Windows Case-Only Rename**: `samefile()` guard for case-only renames on NTFS
- **Rescan After Rename**: Full filesystem rescan after rename execution (single source of truth)
- **Knowledge Base**: `docs/knowledge/` with Windows case-only rename + refresh strategy docs
- **Tests**: 188 PASS (+12 from M11.1 baseline)

## M16
- **AI Memory v2.0**: `AI_MEMORY_PACK.md` auto-generated from 12 source documents
- **Selection Features**: Single-selection mode, selection UX (全选/取消全选), selection-aware rename
- **Governance**: `README_AI.md` as AI memory governance hub

## M11.1
- **Multiple Selection Support**: ExtendedSelection in QTableView, batch rename (file + directory + mixed)
- **Scanner API**: `scan(paths: list[Path])` — multi-path input with deduplication
- **Tests**: 176 PASS (+12 multi-select scenarios)

## M10 Phase 3A
- **Rule Dependency Analysis**: `RuleAnalysis` with `uses_index` / `uses_metadata`, PreviewEngine conditional context
- **MetadataProvider**: Lazy `os.stat()` caching
- **Documentation**: Architecture sync (timestamps → metadata, Directory unified pipeline)
- **Tests**: 164 PASS (+11 RuleAnalysis tests)

## M15 RC
- **AddSuffix Rule**: Independent `add_suffix` handler, no impact on `add_prefix`
- **Undo Validation**: Target missing + double undo edge cases covered
- **RC Regression Matrix**: 32 scenarios (single/2-combo/3-combo/E2E/undo/boundary)
- **AI Memory System**: `docs/AI/` created, 8 initial documents
- **QThread Lifecycle Fix**: RenameWorker moved to instance variable, `closeEvent` timeout
- **Tests**: 152 PASS

## M15
- **AddSuffix Rule**: New `add_suffix` handler + UI entry
- **UX Polish**: Button labels, step numbering, tooltips
- **Tests**: 150 PASS

## M14.2
- **Rule Manager UX**: Button labels ("新建规则"/"删除规则"), step numbering (①②③), tooltips

## M14.1
- **QThread Stabilization**: RenameWorker lifecycle fix

## M14
- **Date Rule**: `source`/`format`/`position`/`separator`, metadata from PreviewEngine context (MetadataProvider)
- **Number Rule Fix**: Folders no longer consume numbering index
- **Tests**: 144 PASS

## M13
- **Insert Rule**: `text` + `at_index`, clamp to bounds
- **Tests**: 131 PASS

## M12
- **Number Rule**: `start`/`step`/`padding`/`position`, pure-function via context
- **Tests**: 122 PASS

## M8-M11
- **Core Pipeline**: Scanner, PreviewEngine, RenamePlanEngine, RenameEngine
- **RuleEngine v1**: replace, remove_text, add_prefix, regex_replace, case, trim
- **UndoEngine**: Single-level undo via OperationLogger
- **Settings**: QSettings-based RenamePolicy
- **i18n**: zh_CN / en_US
- **Packaging**: PyInstaller build
