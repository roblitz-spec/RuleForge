# RuleForge

> **AI-assisted Rule IDE & Rule Execution Platform** — learns reusable transformation rules from examples, executes them through a unified execution architecture.

**Origin**: RuleForge originated from ResourceHub, a batch resource renaming project. During development, the project evolved from task-specific automation toward example-driven rule inference and ultimately became an AI-assisted Rule IDE. File renaming is the initial adapter/use case.

**Development Branch**: [`m11-execution-platform`](https://github.com/roblitz-spec/RuleForge/tree/m11-execution-platform)  
**CI**: [![Test](https://github.com/roblitz-spec/RuleForge/actions/workflows/test.yml/badge.svg)](https://github.com/roblitz-spec/RuleForge/actions/workflows/test.yml)

> 📋 **New to the project?** Start with [`PROJECT_IDENTITY.md`](PROJECT_IDENTITY.md) — the canonical project context.

## Project Status

**Maintenance Mode** — Architecture Baseline Frozen (M12)

| Allowed | Not Allowed |
|---|---|
| Bug fixes | New capability plugins |
| Documentation improvements | Framework refactoring |
| CI / dependency maintenance | Engine refactoring |

Future development requires a new Major Milestone (M13+). See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## 当前状态

| 里程碑 | 状态 | 说明 |
|---|---|---|
| M11 — Execution Platform v1 | ✅ Frozen | 统一执行架构，103 tests |
| M12-A — Batch Execution Foundation | ✅ Frozen | 批量执行基础，27 tests |
| M12-B — Plugin / Extension Framework | ✅ Frozen | 插件与扩展框架，46 tests |
| M12-C — First Official Plugin | ✅ Frozen | RuleValidationPlugin，36 tests |
| M12-D — First Capability Plugin | ✅ Frozen | RollbackPlugin，26 tests |
| M12-E — Scheduler Plugin | ✅ Frozen | SchedulerPlugin，30 tests |
| M12-F — Remote Provider Plugin | ✅ Frozen | RemoteProviderPlugin，32 tests |
| M12-G — Workflow Plugin | ✅ Frozen | WorkflowPlugin，40 tests |
| M12-H — Event Plugin | ✅ Frozen | EventPlugin，38 tests |
| M12-I — Policy Plugin | ✅ Frozen | PolicyPlugin，43 tests |
| M12-J — Validation Plugin | ✅ Frozen | ValidationPlugin，44 tests |
| M12-K — Notification Plugin | ✅ Frozen | NotificationPlugin，44 tests |
| M12-L | 🔄 Planned | |

## 执行平台

RuleForge 提供统一执行架构（Execution Platform v1），支持多种执行引擎：

| 引擎 | 类型 | 说明 |
|---|---|---|
| `string` | 字符转换 | 无状态字符串转换 |
| `rename` | 文件重命名 | 文件系统重命名操作 |
| `dry-run` | 模拟执行 | 验证与冲突检测，不修改文件系统 |
| `inspect` | 执行分析 | 计划摘要、元数据、范围预估 |
| `batch` | 批量执行 | 多规则批量协调执行 |

详见 [`docs/AI/EXECUTION_PLATFORM.md`](docs/AI/EXECUTION_PLATFORM.md)。

## 插件框架

M12-B 建立了官方插件与扩展框架，所有未来扩展能力必须作为 Plugin 实现，不得直接耦合执行平台。

| 组件 | 说明 |
|---|---|
| `Plugin` | 抽象基类，7 个生命周期钩子 |
| `PluginRegistry` | 统一注册、发现、启用/禁用、能力查询 |
| `PluginCapability` | 6 个标准扩展点 |
| `RuleValidationPlugin` | 首个官方插件 — 规则静态校验 |
| `RollbackPlugin` | 首个能力插件 — LIFO 重命名回滚 |
| `SchedulerPlugin` | 执行编排插件 — 延迟/循环任务调度 |
| `RemoteProviderPlugin` | 远程提供者插件 — Provider 注册/发现/选择 |
| `WorkflowPlugin` | 工作流编排插件 — 多步骤流程定义与执行 |
| `EventPlugin` | 事件驱动插件 — Pub/Sub 事件定义与分发 |
| `PolicyPlugin` | 策略插件 — Allow/Deny/Warn 策略评估 |
| `ValidationPlugin` | 校验插件 — 基于规则的数据校验 |
| `NotificationPlugin` | 通知插件 — Channel 注册与消息投递 |

详见 [`docs/architecture/M12B_PLUGIN_FRAMEWORK.md`](docs/architecture/M12B_PLUGIN_FRAMEWORK.md)。

## 技术栈

- Python 3.13+
- PySide6

## 运行

```bash
pip install -r requirements.txt
python main.py
```

## 项目治理

- [项目章程](docs/governance/Project_Charter_v1.0.md) — 项目身份、技术栈、核心能力
- [治理基线](docs/governance/Governance_Baseline_v1.0.md) — 治理文档清单、成熟度评估
- [决策注册表](docs/governance/Decision_Registry_v1.0.md) — 18 项已确认决策 + ADR 索引
- [治理决议](docs/governance/Governance_Resolution_v1.0.md) — PAC-1 Review Findings & Proposed Statements
- [路线图](docs/planning/Roadmap_Refresh.md) — 已完成里程碑、待规划特性
- [PAC-1 发现](docs/PAC/) — 13 份证据发现报告 + 收敛审查

## Current Runtime Architecture

| Layer | Component | Status |
|---|---|---|
| **GUI** | Legacy UI (`ui/main_window.py`) | Stable |
| **Planning** | `RenamePlanEngine` (SSOT) | Stable |
| **Integration** | `ExecutionIntegrationService` (Thin Layer) | Stable |
| **Execution** | `ExecutionPipeline` (Primary Runtime) | Frozen (M11) |
| **Rollback** | `RollbackPlugin` (Unified Rollback) | Frozen (M12-D) |

Execution flow: `GUI` → `RenamePlanEngine` (planning) →
`ExecutionIntegrationService` → `ExecutionPipeline` →
`RenameExecutionEngine` → `RollbackPlugin`.

See [`docs/architecture/runtime_architecture.md`](docs/architecture/runtime_architecture.md)
and [`docs/contracts/execution_integration.md`](docs/contracts/execution_integration.md).

## Documentation Map

### Architecture

| Document | Purpose |
|---|---|
| [Runtime Architecture](docs/architecture/runtime_architecture.md) | Runtime execution flow |
| [Runtime Contract](docs/contracts/execution_integration.md) | Normative integration contract |
| [ADR-007](docs/architecture/adr/007-execution-integration.md) | Execution Integration decision record |

### Maintenance

| Document | Purpose |
|---|---|
| [Legacy Inventory](docs/maintenance/legacy_inventory.md) | Module status catalog |
| [Dependency Audit](docs/maintenance/dependency_audit.md) | Legacy module dependencies |
| [Known Limitations](docs/maintenance/known_limitations.md) | M12 scope limitations |
| [Maintenance Summary](docs/maintenance/maintenance_summary.md) | Maintenance landscape overview |

### Project

| Document | Purpose |
|---|---|
| [PROJECT_IDENTITY](PROJECT_IDENTITY.md) | Canonical project context |
| [Release Notes](docs/releases/M12.1.md) | M12.1 release notes |
| [Closing Report](docs/releases/M12_CLOSING_REPORT.md) | M12 Integration Closure report |
