# 03 — Current Architecture

**PAC-1 Discovery | Date: 2026-07-24**

Source: `docs/AI/ARCHITECTURE.md`, source code inspection, `AGENTS.md`.

---

## 1. Core Modules

### Package Map

```
ResourceHub/
├── main.py                  # Entry point: QApplication → MainWindow
├── scanner/                 # Filesystem scanning
│   └── scanner.py           #   Scanner.scan(paths: list[Path]) → list[FileItem]
├── engine/                  # Transformation & Pipeline
│   ├── rule_engine.py       #   RuleEngine: pure-function text transformation
│   ├── preview_engine.py    #   PreviewEngine: per-item preview with context
│   ├── rename_plan_engine.py#   RenamePlanEngine: target + conflict detection
│   ├── rename_engine.py     #   RenameEngine: Path.rename() execution
│   ├── undo_engine.py       #   UndoEngine: single-level undo
│   ├── rule_analysis.py     #   RuleAnalysis: context dependency declaration
│   ├── operation_logger.py  #   OperationLogger: audit records
│   └── metadata_provider.py #   MetadataProvider: lazy os.stat() cache
├── editor/                  # Rule IDE editing layer
│   ├── edit_session.py      #   EditSession: lifecycle (CREATED/ACTIVE/CLOSED)
│   └── domain_validator.py  #   DomainValidator: UI-independent rule validation
├── validator/               # Input validation
│   └── validator.py         #   File system validation
├── models/                  # Domain data types
│   ├── rule.py              #   Rule (id, name, description, steps, pinned)
│   ├── rule_step.py         #   RuleStep (type, parameters)
│   ├── file_item.py         #   FileItem (path, preview_name, is_directory)
│   ├── rename_plan.py       #   RenamePlan (action, status, message)
│   ├── rename_result.py     #   RenameResult (success, error)
│   ├── rename_policy.py     #   RenamePolicy (FAIL/SKIP/OVERWRITE)
│   ├── preset.py            #   Preset (id, name, description, rules, version)
│   ├── operation_record.py  #   OperationRecord (timestamp, old_path, new_path)
│   ├── session.py           #   SerializableSession (persistence state)
│   ├── validation_result.py #   ValidationResult
│   └── enums.py             #   ItemType enum
├── storage/                 # Persistence
│   ├── repository.py        #   RuleRepository: sole Runtime Source of Truth
│   ├── preset_store.py      #   PresetStore: JSON CRUD at ~/.resourcehub/presets.json
│   ├── json_storage.py      #   JsonStorage: rules.json serialization
│   └── session_store.py     #   SessionStore: session persistence
├── ui/                      # Qt GUI
│   ├── main_window.py       #   MainWindow: orchestration, toolbar, signal routing
│   ├── rule_manager_dialog.py#  RuleManagerDialog: CRUD + RuleStep editing
│   ├── preset_manager_dialog.py# PresetManagerDialog: save/load/delete/rename
│   ├── file_table_model.py  #   FileTableModel: QTableView data provider
│   ├── settings_dialog.py   #   SettingsDialog: RenamePolicy configuration
│   ├── operation_log_dialog.py# OperationLogDialog: undo history display
│   ├── regex_assistant.py   #   RegexAssistant: reference window
│   └── regex_templates.py   #   RegexTemplates: static data
├── workers/                 # QThread workers
│   ├── scan_worker.py       #   ScanWorker: background directory scanning
│   └── rename_worker.py     #   RenameWorker: background rename execution
├── config/                  # Application configuration
│   ├── settings.py          #   Settings: QSettings wrapper (QSettings)
│   └── rules.json           #   Default rule configuration
├── i18n/                    # Internationalization
│   └── translator.py        #   Translator: Qt Linguist .ts loader
├── translations/            # Locale files
│   ├── zh_CN.ts
│   └── en_US.ts
├── tests/                   # Test suite (29 files)
├── scripts/                 # Build scripts
│   └── build.py
└── tools/                   # Development tools
    └── generate_ai_memory.py
```

---

## 2. Module Responsibilities

| Module | Package | Responsibility |
|---|---|---|
| `Scanner` | `scanner/` | Multi-path directory scan, `FileItem` creation, SMB-optimized |
| `RuleEngine` | `engine/` | Pure-function text transformation per RuleStep |
| `PreviewEngine` | `engine/` | Iterate items, construct context via RuleAnalysis, call RuleEngine |
| `RenamePlanEngine` | `engine/` | Target computation, legality check, conflict detection, policy |
| `RenameEngine` | `engine/` | Execute `plan.action` via `Path.rename()` |
| `UndoEngine` | `engine/` | Reverse rename from OperationLogger records |
| `RuleAnalysis` | `engine/` | Declares context needs (`uses_index`, `uses_metadata`) |
| `MetadataProvider` | `engine/` | Lazy metadata (modified, created) caching |
| `EditSession` | `editor/` | Rule editing lifecycle, dirty detection |
| `DomainValidator` | `editor/` | UI-independent Rule / RuleStep validation |
| `RuleRepository` | `storage/` | Sole Runtime Source of Truth for rules |
| `PresetStore` | `storage/` | JSON CRUD for presets (persistent storage only) |
| `MainWindow` | `ui/` | Orchestration, toolbar, signal routing, button wiring |
| `FileTableModel` | `ui/` | Qt Model/View data provider (no filesystem access) |
| `RuleManagerDialog` | `ui/` | CRUD + RuleStep editing + ordering |

---

## 3. Module Relationships

### Call Flow

```
MainWindow (Orchestration)
    ├── Scanner → list[FileItem]
    ├── PreviewEngine (with RuleEngine, RuleAnalysis, MetadataProvider)
    ├── RenamePlanEngine → list[RenamePlan]
    ├── RenameWorker (QThread) → RenameEngine → Path.rename()
    ├── UndoEngine → Path.rename() (reverse)
    ├── RuleRepository ↔ RuleManagerDialog ↔ EditSession
    │       └── PresetManagerDialog
    ├── PresetStore (persist/load only)
    ├── Settings (QSettings wrapper)
    └── FileTableModel (data display)
```

### Dependency Rules

| Rule | Source |
|---|---|
| UI → RenameWorker (QThread) → RenameEngine (never direct) | `ARCHITECTURE.md` § Hard Rules |
| RuleEngine handlers never access filesystem | `ARCHITECTURE.md` § Hard Rules |
| Preview ↔ Rename share same RenamePlan | `ARCHITECTURE.md` § Hard Rules |
| Context fields frozen (`index`, `count`, `metadata`) | ADR-005 |
| RuleEngine = pure function, stateless | ADR-004 |
| Repository = sole Runtime Source of Truth | `AGENTS.md` § 架构原则 |
| PresetStore = persistent storage only | `AGENTS.md` § Rule Presets |
| Scanner: no `Path.resolve()` in hot path | ADR-006 |

---

## 4. Current Boundaries

| Boundary | What's Inside | What's Outside |
|---|---|---|
| `scanner/` | Filesystem scan, FileItem creation | Preview, rename, undo |
| `engine/` | Transformations, context, planning | UI, persistence, filesystem I/O (except rename) |
| `editor/` | Rule editing lifecycle, validation | UI rendering, persistence |
| `storage/` | Domain object persistence | UI, engine logic |
| `ui/` | Qt widgets, signal routing | Business logic, rename execution, filesystem |
| `models/` | Data types (dataclasses) | Behavior, I/O |
| `workers/` | QThread wrappers | Business logic |
| `validator/` | File system validation | Rule validation (that's in editor/) |

---

## 5. Potential Architectural Debt

| ID | Item | Evidence | Severity |
|---|---|---|---|
| TD-003 | RuleManagerDialog God Class (694 lines) | `docs/AI/CURRENT_STATUS.md` | LOW |
| TD-007 | MainWindow approaching God Class (550 lines) | `docs/AI/CURRENT_STATUS.md` | LOW |
| TD-011 | FileItem naming ambiguity (files + dirs) | `docs/AI/CURRENT_STATUS.md` | LOW |
| TD-018 | Validator refactor needed (reimplements inline) | `docs/AI/CURRENT_STATUS.md` | LOW |
| **MISSING** | "Master Design" document for `editor/` package | `editor/` module docstrings | MEDIUM |

---

## 6. Current vs. Planned Architecture

| Item | Status | Evidence |
|---|---|---|
| Core pipeline (Scanner → Rename → Undo) | ✅ Implemented | `ARCHITECTURE.md` + source |
| RuleEngine pure-function framework | ✅ Implemented | ADR-004, `engine/rule_engine.py` |
| Context Contract | ✅ Implemented | ADR-005, `engine/preview_engine.py` |
| RuleAnalysis dependency declaration | ✅ Implemented | `engine/rule_analysis.py` |
| Rule Presets | ✅ Implemented (M8) | `storage/preset_store.py` |
| `editor/` package (Rule IDE layer) | ✅ Implemented, partially | `editor/` (382 lines) |
| Filter System | ❌ Planned (P1) | `docs/AI/NEXT_MILESTONE.md` |
| EXIF Date | ❌ Planned (P2) | `docs/AI/NEXT_MILESTONE.md` |
| Variables | ❌ Planned (P4) | `docs/AI/NEXT_MILESTONE.md` |
| Multi-level Undo | ❌ Deferred | ADR-002 |
| Dark Mode | ❌ Deferred | `docs/AI/NEXT_MILESTONE.md` |
| Plugin System | ❌ Not planned | `docs/AI/KNOWN_LIMITATIONS.md` |

---

## 7. Architecture Diagram

```
┌──────────┐    ┌─────────────┐    ┌──────────────────┐    ┌──────────────┐    ┌─────────────┐
│  Scanner  │───▶│  Preview    │───▶│  RenamePlan      │───▶│  Rename      │───▶│  Undo       │
│           │    │  Engine     │    │  Engine          │    │  Engine      │    │  Engine     │
│ os.scandir│    │  RuleEngine │    │  Conflict detect │    │  Path.rename │    │  Reverse    │
└──────────┘    │  + context  │    │  Policy apply    │    │  (QThread)   │    │  rename     │
                └─────────────┘    └──────────────────┘    └──────────────┘    └─────────────┘
                       │                                           │
                       ▼                                           ▼
                ┌─────────────┐                          ┌──────────────────┐
                │ RuleAnalysis│                          │ OperationLogger  │
                │ + Context   │                          │ (audit records)  │
                └─────────────┘                          └──────────────────┘

Persistent State:                    UI Layer:
┌──────────────────┐                ┌──────────────────────────────┐
│ RuleRepository   │◀──────────────│ MainWindow (orchestration)    │
│ (runtime truth)  │               │   ├── RuleManagerDialog       │
└────────┬─────────┘               │   ├── PresetManagerDialog     │
         │                         │   ├── FileTableModel          │
         ▼                         │   ├── SettingsDialog          │
┌──────────────────┐               │   └── RegexAssistant          │
│ PresetStore      │               └──────────────────────────────┘
│ Settings         │                          │
│ SessionStore     │                          ▼
└──────────────────┘               ┌──────────────────────────────┐
                                   │ editor/ (Rule IDE layer)      │
                                   │   ├── EditSession             │
                                   │   └── DomainValidator         │
                                   └──────────────────────────────┘
```

---

**Confidence**: HIGH (architecture documented in `ARCHITECTURE.md`, verified by source code inspection)
