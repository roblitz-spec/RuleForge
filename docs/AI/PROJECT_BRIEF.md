# ResourceHub — Project Brief

## What

ResourceHub is a Windows desktop batch file rename tool built with Python 3.12+ and PySide6.

## Why

To provide a safe, previewable, rule-based batch rename experience with full Unicode support and undo capability.

## Current Version

**M11.2** — Sortable Table, Context Menu, Pin Rules, Regex Assistant

## Completed Capabilities

- **Scanner**: Multi-path input (`scan(paths: list[Path])`), file + directory + mixed, non-recursive via `os.scandir()`, SMB-optimized (no `resolve()`)
- **Rule Engine**: 10 RuleStep types (replace, remove_text, regex_replace, case, trim, number, insert, date, add_prefix, add_suffix)
- **Rule Analysis**: Rule dependency pre-analysis (`uses_index` / `uses_metadata`), context constructed on demand
- **Preview Engine**: Real-time preview with context (index, metadata via MetadataProvider)
- **RenamePlan Engine**: Unified plan generation + conflict detection + legality checks, Windows case-only rename support (`samefile()`)
- **Rename Engine**: Policy-based execution (FAIL/SKIP/OVERWRITE), rescan after rename
- **Undo Engine**: Single-level undo via OperationLogger
- **Multi Selection**: ExtendedSelection in QTableView, batch rename with single Undo
- **Rule Manager**: Full CRUD + RuleStep editor with type selection, parameter editing, ordering, pin rules, regex assistant
- **File Table**: Sortable columns, context menu
- **Settings**: QSettings-based RenamePolicy persistence
- **i18n**: zh_CN / en_US via Qt Linguist .ts files
- **Packaging**: PyInstaller build with translations

## Current Stage

M11.2 Stabilization. Architecture stable.

## Next Stage

See `NEXT_MILESTONE.md`.
