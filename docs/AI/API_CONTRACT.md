# RuleForge — Public API Contract

> **Version**: 1.0 (M10.5-E freeze)
> **Policy**: Backward compatible within 1.x. Breaking changes require ADR.

## Public API

These types and methods are the stable contract for all external
consumers: CLI, SDK, REST API, GUI, and automation.

### Orchestration

| Entry Point | Module | Description |
|---|---|---|
| `RuleWorkflow` | `engine.rule_workflow` | Single orchestration entry point |
| `WorkflowResult` | `engine.rule_workflow` | Pipeline outcome (success, errors, stage results) |

#### RuleWorkflow

```python
class RuleWorkflow:
    @staticmethod
    def infer(examples: list[tuple[str, str]], name: str = "Inferred Rule") -> InferredRule | None: ...

    @staticmethod
    def open_session(inferred_rule: InferredRule, store: object | None = None) -> RuleSession: ...

    @staticmethod
    def inspect(rule: Rule) -> RuleInspection: ...

    @staticmethod
    def execute(rule: Rule, inputs: list[str]) -> list[str]: ...

    def run(self, examples: list[tuple[str, str]], name: str = "Inferred Rule",
            store: object | None = None) -> WorkflowResult: ...
```

**Contract**: `RuleWorkflow` is the **only** orchestration entry point.
No consumer may call `RuleSession`, `RuleInspection`, or `preview_rule`
directly as a workflow entry point.  All workflow traversal goes
through `RuleWorkflow`.

#### WorkflowResult

```python
@dataclass
class WorkflowResult:
    inferred_rule: InferredRule | None   # from infer() stage
    inspection: RuleInspection | None    # from inspect() stage
    validation: SessionValidationResult | None  # from validate() stage
    preview: ExamplePreviewResult | None # from preview() stage
    outputs: list[str]                   # from execute() stage
    errors: list[str]                    # collected error messages
    success: bool                        # True iff no errors

    def add_error(self, message: str) -> None: ...
```

**Contract**:
- `success` is deterministic: `True` iff `errors` is empty
- `errors` is never `None` (always a list)
- Stage results are `None` when the stage was not reached
- `outputs` is `[]` when execution didn't run

### Session

| Type | Module | Description |
|---|---|---|
| `RuleSession` | `engine.rule_session` | Mutable workflow state (owned by RuleWorkflow) |
| `SessionState` | `models.session_state` | Explicit lifecycle state enum |
| `InvalidStateTransition` | `models.session_state` | Raised on invalid state transitions |
| `SessionValidationResult` | `models.session_validation` | Validation outcome |

#### SessionState

```
NEW → INFERRED → EDITING → VALIDATED → PREVIEW_READY → COMMITTED → EXECUTED
```

`EXECUTED` is terminal.  Same-state transitions are idempotent.

### Domain Models

| Type | Module | Description |
|---|---|---|
| `InferredRule` | `models.inferred_rule` | Rule + inference metadata |
| `Rule` | `models.rule` | Rule with ordered `RuleStep` list |
| `RuleStep` | `models.rule` | Single transformation step (type + parameters) |
| `RuleLifecycle` | `models.rule_lifecycle` | Rule maturity: INFERRED → EDITABLE → TESTED → EXECUTABLE |

### Inspection & Preview

| Type | Module | Description |
|---|---|---|
| `RuleInspection` | `engine.rule_inspector` | Structured rule metadata |
| `ExamplePreviewResult` | `engine.preview_pipeline` | Preview output |
| `PreviewEntry` | `engine.preview_pipeline` | Single preview entry (input → output → expected → match) |

#### RuleInspection

```python
@dataclass
class RuleInspection:
    rule_id: str
    rule_name: str
    step_count: int
    steps: list[StepInfo]       # per-step detail
    uses_index: bool
    uses_metadata: bool
    is_empty: bool
    warnings: list[str]
```

#### ExamplePreviewResult

```python
@dataclass
class ExamplePreviewResult:
    entries: list[PreviewEntry]
    all_match: bool

@dataclass
class PreviewEntry:
    input_text: str
    output_text: str
    expected: str | None
    match: bool | None
```

### Inference

| Function | Module | Description |
|---|---|---|
| `infer_rule(examples, name)` | `engine.rule_inference` | Infer a Rule from example pairs |

Returns `InferredRule | None`.  `None` means no transformation needed.

#### Public helper functions

```python
from models.session_state import can_transition, transition

def can_transition(current: SessionState, target: SessionState) -> bool: ...
def transition(current: SessionState, target: SessionState) -> SessionState: ...
```

### Exceptions

| Exception | Module | When |
|---|---|---|
| `InvalidStateTransition` | `models.session_state` | Invalid state transition attempted |
| `RuntimeError` | builtins | Session already open, session not open |
| `EngineNotFoundError` | `engine.engine_registry` | Unknown engine name requested |
| `DuplicateEngineError` | `engine.engine_registry` | Engine name already registered |

**Contract**: These four exception types are part of the public API.
Internal validation issues and implementation errors are reported
through `WorkflowResult.errors` or `SessionValidationResult`, not
through exceptions.

### Execution Pipeline

| Type | Module | Description |
|---|---|---|
| `ExecutionContext` | `engine.execution_context` | Immutable execution request (rule + targets + options) |
| `ExecutionResult` | `engine.execution_result` | Stable execution outcome (outputs, diagnostics, timing) |
| `ExecutionEngine` | `engine.execution_engine` | Abstract engine interface (prepare/execute/cleanup) |
| `ExecutionPipeline` | `engine.execution_pipeline` | Coordinates context → engine → result |
| `StringTransformEngine` | `engine.string_transform_engine` | Default headless string transform engine |
| `RenameExecutionEngine` | `engine.rename_execution_engine` | Filesystem rename engine (prepare→conflict detect→execute) |
| `DryRunExecutionEngine` | `engine.dry_run_execution_engine` | Non-mutating validation (identical conflict detection) |
| `InspectionExecutionEngine` | `engine.inspection_execution_engine` | Execution analysis (summary, metadata, scope estimation) |
| `FilesystemAdapter` | `engine.filesystem_adapter` | Abstract filesystem (testing, dry run) |
| `RealFilesystemAdapter` | `engine.filesystem_adapter` | Production pathlib adapter |
| `EngineRegistry` | `engine.engine_registry` | Named engine discovery and selection |
| `ExecutionTrace` | `engine.execution_trace` | Execution lifecycle trace (Pipeline-owned) |
| `ExecutionMetrics` | `engine.execution_metrics` | Structured execution statistics |
| `ExecutionDiagnostics` | `engine.execution_diagnostics` | Structured diagnostics builder |

#### ExecutionContext

```python
@dataclass(frozen=True)
class ExecutionContext:
    rule: Rule
    targets: list[str]      # string inputs or file paths
    options: dict[str, object]  # runtime configuration
    target_count: int       # derived: len(targets)
```

#### ExecutionResult

```python
@dataclass
class ExecutionResult:
    success: bool
    outputs: list[str]
    actions_executed: int
    actions_skipped: int
    errors: list[str]
    diagnostics: dict[str, object]  # engine-specific metadata
    duration_ms: float | None       # wall-clock execution time
    total_actions: int              # derived: executed + skipped
```

#### RuleWorkflow integration

```python
class RuleWorkflow:
    @staticmethod
    def execute_with_engine(
        rule: Rule, targets: list[str],
        engine: ExecutionEngine | None = None,
    ) -> ExecutionResult: ...
```

`engine=None` defaults to `StringTransformEngine`.

#### RenameExecutionEngine

```python
class RenameExecutionEngine(ExecutionEngine):
    def __init__(self, fs: FilesystemAdapter | None = None): ...

    # prepare: validate sources exist, compute target names via
    #          preview_rule, detect duplicate/existing conflicts
    def prepare(self, context: ExecutionContext) -> None: ...

    # execute: rename files in deterministic source-path order,
    #          fail-fast on first error, return ExecutionResult
    #          with operations journal in diagnostics
    def execute(self, context: ExecutionContext) -> ExecutionResult: ...

    # cleanup: clear internal operation journal
    def cleanup(self, context: ExecutionContext) -> None: ...
```

Execution order: source paths sorted ascending.
Conflict detection: duplicate targets → fatal, destination exists → fatal.
Journal: `result.diagnostics["operations_journal"]` is a list of
`{"source", "target", "status", "error"}` per operation.

#### Engine Comparison

| Engine | Filesystem Mutation | Conflict Detection | Diagnostics |
|---|---|---|---|
| `StringTransformEngine` | No | No | preview results |
| `RenameExecutionEngine` | **Yes** | Yes (fatal) | journal, conflict count |
| `DryRunExecutionEngine` | No | Yes (fatal) | journal, would_rename, would_skip |
| `InspectionExecutionEngine` | No | Yes (non-fatal) | journal, stems, scope, metadata |

#### EngineRegistry

```python
class EngineRegistry:
    @classmethod
    def default(cls) -> EngineRegistry: ...
    def register(self, name: str, engine_cls: Type[ExecutionEngine]) -> None: ...
    def replace(self, name: str, engine_cls: Type[ExecutionEngine]) -> None: ...
    def create(self, name: str) -> ExecutionEngine: ...
    def names(self) -> list[str]: ...
    def is_registered(self, name: str) -> bool: ...
```

Built-in engines: `"string"`, `"rename"`, `"dry-run"`, `"inspect"`.
`create()` produces a new instance per call — no shared mutable state.
`register()` raises `DuplicateEngineError` on duplicate names.

#### RuleWorkflow execution methods

```python
class RuleWorkflow:
    # Direct engine injection (M11-A, backward compatible)
    @staticmethod
    def execute_with_engine(
        rule: Rule, targets: list[str],
        engine: ExecutionEngine | None = None,
    ) -> ExecutionResult: ...

    # Named engine resolution via registry (M11-D)
    @staticmethod
    def execute_named(
        rule: Rule, targets: list[str],
        engine_name: str = "string",
        registry: EngineRegistry | None = None,
    ) -> ExecutionResult: ...

    # Plain string output (backward compatible, pre-M11)
    @staticmethod
    def execute(rule: Rule, inputs: list[str]) -> list[str]: ...
```

### Observability (M11-E)

Every `ExecutionPipeline.run()` produces:

- **`ExecutionTrace`**: lifecycle events (execution/validation/prepare/execute/cleanup), timestamps, per-stage duration. Pipeline-owned — engines never create traces.
- **`ExecutionMetrics`**: `files_scanned`, `files_selected`, `files_modified`, `files_skipped`, `conflict_count`, `error_count`, `duration_ms` + engine-specific `extra`.
- **`ExecutionDiagnostics`**: structured builder with `errors[]`, `warnings[]`, `conflicts[]`, `journal[]`, `metadata{}`.

All three are attached to `ExecutionResult` as `trace`, `metrics`, and `diagnostics` fields.  Existing callers are unaffected — new fields are optional and additive.

```python
result = ExecutionPipeline.run(context, engine)
result.trace        # ExecutionTrace | None
result.metrics      # ExecutionMetrics | None
result.diagnostics  # dict[str, object] (backward compat)

### CLI

| Command | Contract |
|---|---|
| `ruleforge workflow run <examples>` | `RuleWorkflow.run()` — full pipeline |
| `ruleforge workflow infer <examples>` | `RuleWorkflow.infer()` → JSON to stdout |
| `ruleforge workflow execute <rule> <ins>` | `RuleWorkflow.execute()` |

**Output contract**:
- `infer` prints JSON to stdout (machine-readable, compatibility commitment)
- Status/help messages to stderr (not a compatibility guarantee)
- Exit codes: `0` = success, `1` = failure

## Internal API (not part of public contract)

These modules may change without notice.  Consumers must not depend
on them directly.

| Module | Role |
|---|---|
| `editor.edit_session.EditSession` | Working-copy management (session internal) |
| `editor.domain_validator.DomainValidator` | Rule validation (called by session) |
| `storage.inferred_rule_store.InferredRuleStore` | Persistence (called by session) |
| `engine.rule_engine` | Batch rename engine (adapter) |
| `engine.rename_engine` | Filesystem rename execution |
| `engine.rename_plan_engine` | Rename plan generation |
| `engine.preview_engine` | Preview generation for batch rename |
| `engine.rule_analysis` | Analysis warnings |
| `engine.metadata_provider` | File metadata |
| `engine.operation_logger` | Operation logging |
| `engine.undo_engine` | Undo support |
| `ui.*` | GUI (PySide6) |

## Compatibility Policy

1. **Public API is backward compatible within 1.x.**
2. **New capability extends, never replaces** existing public API.
3. **Breaking changes require**: ADR, migration path, new major version
   (or explicit architectural approval during pre-1.0 development).
4. **Machine-readable output formats** (infer JSON, exit codes) are
   compatibility commitments.
5. **Human-readable messages** are not guaranteed stable.
6. **Reserved exit codes**: `0` success, `1` failure.  Codes `2`–`127`
   reserved for future workflow categories.
