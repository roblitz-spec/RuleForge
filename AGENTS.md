# RuleForge — 开发参考

> 治理文档：`docs/AI/CONSTITUTION.md`（宪法）、`docs/AI/ENGINEERING_BASELINE.md`（工程基线）、`docs/AI/MILESTONE_CHECKLIST.md`（里程碑检查清单）、`docs/AI/API_CONTRACT.md`（公共 API）、`docs/AI/ADR_INDEX.md`（ADR 索引）

## Git 基线

| Tag | 内容 |
|---|---|
| `M2-complete` | EditSession, WorkingCopy, UI Integration |
| `M3-complete` | Commit, Undo/Redo, Preview Isolation |
| `M4-complete` | Auto Save, Unsaved Changes Warning, Session Persistence |
| `M4.1-complete` | Architecture Alignment Patch |
| `M5-complete` | Smart Previews & Analysis Warnings，356 tests |
| `M6-complete` | Rule Duplication（复制规则），384 tests |
| `M7-complete` | Architecture Consolidation（架构整合），398 tests |
| `M8-complete` | Rule Presets（规则预设），447 tests |
| `M9-complete` | RuleInference Engine，30 tests |
| `M10-complete` | Rule Model, Session, Workflow, Lifecycle, E2E, CLI, API Freeze, Constitution，164 tests |
| `M11-A-complete` | Execution Pipeline，24 tests |
| `M11-B-complete` | Rename Execution Engine，13 tests |
| `M11-C-complete` | Dry Run & Inspection Engine，15 tests |
| `M11-D-complete` | Engine Registry，23 tests |
| `M11-E-complete` | Execution Observability，28 tests |
| `M11-complete` | Execution Platform v1，103 tests，743 total——架构基线冻结 |
| `M12-A-complete` | Batch Execution Foundation，27 tests |
| `M12-B-complete` | Plugin / Extension Framework，46 tests |
| `M12-C-complete` | First Official Plugin (RuleValidationPlugin)，36 tests |
| `M12-D-complete` | First Capability Plugin (RollbackPlugin)，26 tests |
| `M12-E-complete` | Scheduler Plugin (SchedulerPlugin)，30 tests |
| `M12-complete` | Number Rule 完成，122 tests |
| `M13-complete` | Insert Rule 完成，131 tests |
| `M14-complete` | Date Rule 完成，144 tests |
| `M15-complete` | AddSuffix Rule 完成，AI Memory 系统建立 |
| `M16-complete` | AI Memory v2.0 Governance，Selection Features |

## RuleStep 类型总览

| type | 中文 | 参数 | 默认值 |
|---|---|---|---|
| `replace` | 文本替换 | `from`, `to` | `""`, `""` |
| `remove_text` | 删除文本 | `text` | `""` |
| `regex_replace` | 正则替换 | `pattern`, `replacement`, `flags` | `""`, `""`, `""` |
| `case` | 大小写转换 | `mode` | `"upper"` |
| `trim` | 去除空白 | `mode` | `"both"` |
| `number` | 编号 | `start`, `step`, `padding`, `position` | `"1"`, `"1"`, `"3"`, `"prefix"` |
| `insert` | 插入文本 | `text`, `at_index` | `""`, `"0"` |
| `date` | 日期 | `source`, `format`, `position`, `separator` | `"modified"`, `"%Y-%m-%d"`, `"prefix"`, `"_"` |
| `add_prefix` | 添加前缀 | `text` | `""` |

## Insert Rule 行为规范

- `at_index = 0` → 插入到开头
- `at_index = N (0 < N ≤ len)` → 插入到第 N 个字符后
- `at_index > len` → clamp 到末尾
- `at_index < 0`（任意负数）→ clamp 到末尾
- `text = ""` → 不改变原文字
- Step 顺序严格按列表执行，Insert 不例外

## Date Rule 行为规范

- `source` 从 context `metadata`（MetadataProvider）中获取时间戳
- 当前仅实现 `modified`；`created`/`exif`/`now` 预留
- 未知 source → 返回原名（不 fallback）
- context 缺失 → 返回原名（纯函数，不调用 `datetime.now()`）
- `format` 使用 Python `strftime` 格式
- `separator = ""` → 日期与文件名直连

## Number Rule 行为规范

- `index` 由 PreviewEngine 提供（1-based），非 Python 下标
- 无 context 时默认 `index = 1`
- 计算公式：`number = start + (index - 1) * step`
- `padding = 0` → 不补零
- RuleEngine 保持无状态，不存储计数器

## RuleInference（M9）

- `engine/rule_inference.py`：纯函数模块，从 (original, desired) 示例对推导 RuleStep
- 算法：候选生成 → 交集 → 组合搜索（深度 3）
- 检测能力：case（4 模式）、trim（3 模式）、replace/remove_text（SequenceMatcher 差分）、add_prefix/add_suffix、insert
- 多步骤流水线：自动发现组合（如 trim → case、replace → case）

## RuleSession Lifecycle（M10.5-B）

- `models/session_state.py`：`SessionState` 显式状态模型，强制转移验证
- 状态：`NEW → INFERRED → EDITING → VALIDATED → PREVIEW_READY → COMMITTED → EXECUTED`
- 无效转移 → `InvalidStateTransition`（带描述信息）
- 失败操作不推进状态；同状态转移为幂等（无操作）
- `commit()` 自动调用 `validate()`，验证失败拒绝提交
- `RuleLifecycle` 保留用于存储成熟度追踪（与 `SessionState` 分离）

## RuleWorkflow（M10.5 + M10.5-C）

- `engine/rule_workflow.py`：薄编排层，组合已有引擎能力
- `infer()` → `open_session()` → `validate()` → `preview()` → `commit()` → `finalize()` → `execute()`
- `run()` 完整流水线便捷方法
- RuleWorkflow 不拥有状态 — RuleSession 是唯一权威可变对象
- E2E 验证：14 tests 覆盖成功路径、失败路径、状态一致性、产物验证
- CLI 集成：`cli/workflow_cli.py` 薄包装层，`run`/`infer`/`execute` 命令，18 tests
- API Freeze：公共 API 契约冻结于 `docs/AI/API_CONTRACT.md`，ADR-012 记录兼容性策略
- Execution Pipeline：M11-A 引入 `ExecutionContext` + `ExecutionEngine` + `ExecutionPipeline` + `ExecutionResult`，24 tests
- Rename Execution Engine：M11-B `RenameExecutionEngine` + `FilesystemAdapter`，13 tests
- Dry Run & Inspection Engine：M11-C `DryRunExecutionEngine` + `InspectionExecutionEngine`，15 tests
- Engine Registry：M11-D `EngineRegistry` + `execute_named()`，23 tests
- Execution Observability：M11-E `ExecutionTrace` + `ExecutionMetrics` + `ExecutionDiagnostics`，28 tests
- Platform Freeze：M11-F `EXECUTION_PLATFORM.md` 最终架构基线，6 条冻结设计原则

## 架构原则

- RuleEngine：纯函数，无状态，通过 `context` 参数传递索引
- RenamePlanEngine：统一生成计划 + 冲突检测 + 合法性校验
- RenameEngine：仅按 `plan.action` 执行，不重复决策
- Preview ↔ Rename 共享同一份 RenamePlan
- RuleInference：纯函数，无状态，组合搜索
- RuleSession：唯一可变状态所有者，SessionState 强制转移
- RuleWorkflow：无状态编排层，读取 SessionState 但不写入
- ExecutionPipeline：执行协调层，验证 → 准备 → 执行 → 收集 → 清理，拥有 Trace
- ExecutionEngine：抽象引擎接口（prepare/execute/cleanup），不操纵工作流状态
- EngineRegistry：命名引擎注册与选择，解耦 RuleWorkflow 与具体引擎
- 可观测性：ExecutionTrace（Pipeline 拥有）+ ExecutionMetrics（结构化指标）+ ExecutionDiagnostics

## M11 冻结设计原则（Execution Platform v1）

以下原则为架构约束，M12+ 不得违反：

1. **Pipeline 执行，Registry 选择** — Pipeline 不解引 Engine；Registry 不执行
2. **Engine 实现行为，不实现编排** — Engine 拥有执行语义，不控制工作流
3. **规划与执行分离** — `build_rename_plan()` 验证和冲突检测；Engine 执行
4. **可观测性属于执行生命周期** — Trace 由 Pipeline 创建和填充
5. **ExecutionResult 是统一输出契约** — 所有 Engine 产生相同结果类型
6. **新执行模式是 Engine，不是 Pipeline 分支** — 通过新 ExecutionEngine 扩展

详见 `docs/AI/EXECUTION_PLATFORM.md`

## Batch Execution (M12-A)

- `ExecutionBatch`：有序 `BatchItem` 容器，含 `stop_on_error` / `validate_first` 策略
- `BatchItem`：单个执行单元（rule + targets + engine_name + label + options）
- `BatchExecutor.run()`：顺序迭代 BatchItem，每项通过 `ExecutionPipeline.run()` 执行
- `BatchResult`：聚合层——每项保存完整 `ExecutionResult`，不修改 `ExecutionResult` 契约
- `BatchExecutionEngine`：将 batch 包装为 `ExecutionEngine`（通过 context.options["_batch_definition"] 传递）
- 反嵌套：`BatchItem.engine_name` 不得为 `"batch"` → `ValueError`
- `RuleWorkflow.execute_batch()`：薄委托层

## Plugin / Extension Framework (M12-B)

- `plugins/`：独立包，零耦合 engine/
- `Plugin` (ABC)：生命周期钩子（discover/load/initialize/activate/deactivate/unload），默认 no-op
- `PluginMetadata` (frozen)：name、version、capabilities、dependencies
- `PluginCapability` (enum)：RULE_DISCOVERY、VALIDATION、EXECUTION_HOOK、BATCH_HOOK、RESULT_PROCESSING、OUTPUT_EXPORT
- `PluginContext` (frozen)：只读上下文，含 registry 引用 + opaque data
- `PluginRegistry`：注册/注销、启用/禁用、激活/停用、capability 查询、依赖校验
- 生命周期：LOADED → ENABLED → ACTIVE → ENABLED → LOADED
- 错误隔离：单个插件 `on_activate` 失败不影响其他插件
- 扩展点定义为契约 — 实际 hook 调用在后续 Milestone 中连接
- Rollback、Scheduler、Remote Provider 将作为 Plugin 实现，而非核心平台修改

## First Official Plugin (M12-C)

- `RuleValidationPlugin`：首个官方插件，`plugins/rule_validation_plugin.py`
- Capability：`VALIDATION`
- 检测：空步骤（warning）、未知类型（error）、缺失必需参数（error）、无效正则（error）、无效 case/trim mode（error）、非整数 number 参数（error）
- `ValidationResult` / `ValidationIssue`：插件自有数据模型
- 独立可调用 API：`plugin.validate(rule) → ValidationResult`
- 全生命周期验证通过：register → enable → activate → deactivate → disable → unregister
- Plugin Framework 无需任何修改即可支撑官方插件 —— 冻结契约完全满足需求

## First Capability Plugin (M12-D)

- `RollbackPlugin`：首个能力插件，`plugins/rollback_plugin.py`
- Capability：`EXECUTION_HOOK`
- 核心 API：`record_rename(old, new)` + `rollback() → RollbackResult`
- LIFO 回滚：反向逆序恢复所有已记录重命名
- 安全处理：文件已不存在 → skip、目标已存在 → skip、OS error → failed
- `RollbackResult`：restored、failed、skipped 分类 + success_rate
- Lifecycle vs Business State：`deactivate()` 保留历史，`unregister()` 清理资源
- 26 tests，863 total

## Scheduler Plugin (M12-E)

- `SchedulerPlugin`：执行编排插件，`plugins/scheduler_plugin.py`
- Capability：`EXECUTION_HOOK`
- 核心 API：`schedule_once(delay)` + `schedule_recurring(interval, max_runs)` + `cancel()` + `cancel_all()`
- Trigger Model：once（单次延迟）、recurring unlimited（无限循环）、recurring max_runs=N（有限次）
- 回调异常隔离：单个回调失败不影响其他任务调度
- deactivate() 自动 cancel_all()，资源释放
- Scheduler / Execution 职责分离：Scheduler 负责 timing policy，Execution Platform 负责执行
- 30 tests，893 total

## Context Contract

RuleEngine 与 PreviewEngine 之间通过 `context` 字典通信。

**已冻结字段（不得修改名称或语义）**：

| 字段 | 类型 | 语义 | 使用者 |
|---|---|---|---|
| `context["index"]` | `int` | 当前文件序号（1-based） | Number Rule |
| `context["count"]` | `int` | 文件总数 | 预留 |
| `context["metadata"]` | `MetadataProvider` | 惰性元数据提供器（`modified`/`created`） | Date Rule |

**扩展规则**：
- 新增 MetadataProvider 属性允许
- 不得修改已冻结字段的名称、类型或语义
- 未知字段或缺失字段 → handler 返回原名，不得崩溃

## Development Workflow

每个 Milestone 统一流程：

### 1. Implementation（实现）
- 小步迭代，每次只完成一个明确目标
- 保持 RuleEngine 纯函数、无状态设计
- 新增 Rule 类型只需注册 `_HANDLERS` + `_STEP_TYPES`，不改架构

### 2. Automated Tests（自动化测试）
- 为新增功能补充对应测试
- 覆盖：默认参数、边界值、Rule 顺序、保存/加载、Preview↔Rename 一致性
- 全部测试通过后进入下一阶段

### 3. Validation（产品行为验证）
- 验证默认参数与产品规范一致
- 验证边界条件（空值、超长、负数等）
- 验证 Rule 顺序语义（Step A → Step B ≠ Step B → Step A）
- 验证保存/加载 roundtrip
- 验证 Preview 显示与实际 Rename 结果一致

### 4. Smoke Test（真实使用验证）
- 使用真实目录进行手工验证
- 验证完整 Rename 流程（Preview → Plan → Rename → 文件确认）
- 验证 UI 行为（不重扫、Preview 自刷新、按钮状态）

### 5. Git Tag（创建基线）
- 当前 Milestone 完成后创建稳定基线
- 命名：`Mxx-complete`
- 目的：后续可快速回退定位

### 6. Feature Freeze（功能冻结）
- 当前 Milestone 完成后冻结相关模块
- 除真实 Bug 外，不修改已冻结模块
- 新功能优先通过新增模块或新增 Rule 实现

### 7. Update AGENTS.md（更新文档）
- 更新新增 Rule 类型、默认参数、行为规范
- 更新 Git 基线记录
- 更新架构说明（如有变化）

### 8. Next Milestone（进入下一阶段）
- 以上步骤全部完成后，方可开始下一 Milestone 开发

### 开发原则

- **小步迭代**：每次只完成一个明确目标
- **测试先行**：先写测试，再写实现，或同步进行
- **稳定基线**：每个 Milestone 锁 Tag、锁行为
- **功能冻结**：完成后不轻易改，只能 Bug Fix
- **文档同步**：行为变更必须更新 AGENTS.md

## Rule Presets（M8）

### 预设数据模型

- `Preset` dataclass：`id`（唯一标识）、`name`、`description`、`rules: list[Rule]`、`version=1`
- `PresetStore`：JSON 持久化存储于 `~/.resourcehub/presets.json`
- 提供完整 CRUD：`save` / `save_all` / `load_all` / `delete` / `rename`

### 预设管理对话框

- `PresetManagerDialog`（QDialog）：保存 / 加载 / 删除 / 重命名
- 操作前通过 `EditSession` 脏状态守卫防止未保存修改丢失
- `Repository.replace_rules()`：以原子方式替换全部 Rule 列表

### 工具栏预设选择器

- 主窗口工具栏 QComboBox：下拉显示全部已保存预设
- 切换预设立即同步 `Repository` → 刷新规则下拉框 → 刷新预览
- "管理预设"按钮打开 `PresetManagerDialog`

### 启动恢复

- `Settings.get_last_preset_id()` / `set_last_preset_id()`：基于 QSettings 持久化
- 应用启动时自动恢复上次使用的预设（`_restore_last_preset()`）
- 预设已删除或不存在 → 静默跳过

### 架构约束

- `Repository` 始终为唯一运行时真源
- `PresetStore` 仅为持久化存储，不参与运行时状态
- `Settings` 仅存储预设标识符（元数据），不存储规则数据
- 加载预设通过 `Repository.replace_rules()`（公有 API）

## One Milestone, One Core Feature

每个 Milestone 只引入一个核心能力。

目的：
- 控制变更范围
- 降低回归风险
- 提高测试覆盖质量
- 简化 Validation
- 建立清晰稳定的 Git 基线
- 方便问题定位与回滚

一个 Milestone 只完成一个新的 Rule、一个新的核心模块或一个独立的新能力。
如果某项能力较大，应拆分为多个 Milestone，而不是一次完成。

**关闭条件**（全部满足方可进入下一 Milestone）：

1. 功能实现完成
2. 自动化测试通过
3. Validation 完成
4. Smoke Test 完成
5. Git Tag 已创建
6. Feature Freeze 已执行
7. AGENTS.md 已更新

## Backward Compatibility

除非属于 Major Version 或经明确批准的架构升级，否则必须保持向后兼容。

原则：
- 已保存的 Rule 配置（`rules.json`）必须保持兼容
- 已公开的参数名称不得随意修改
- 已冻结 Rule 的行为不得改变
- 新功能应以扩展方式实现（新增 handler、新增 step type），而不是修改已有语义
- 新增 Rule 不得破坏已有 Rule 的行为

如果确实需要破坏兼容性，必须同时完成：

1. 在当前 Milestone 中明确说明变更原因
2. 提供迁移方案
3. 更新 AGENTS.md
4. 创建新的稳定 Git Tag，作为新的兼容性基线
