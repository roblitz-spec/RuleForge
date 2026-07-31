# RuleForge

> **AI-assisted Rule IDE & Rule Execution Platform** — learns reusable transformation rules from examples, executes them through a unified execution architecture.

**Origin**: RuleForge originated from ResourceHub, a batch resource renaming project. During development, the project evolved from task-specific automation toward example-driven rule inference and ultimately became an AI-assisted Rule IDE. File renaming is the initial adapter/use case.

## 执行平台

RuleForge 提供统一执行架构（Execution Platform v1），支持多种执行引擎：

| 引擎 | 类型 | 说明 |
|---|---|---|
| `string` | 字符转换 | 无状态字符串转换 |
| `rename` | 文件重命名 | 文件系统重命名操作 |
| `dry-run` | 模拟执行 | 验证与冲突检测，不修改文件系统 |
| `inspect` | 执行分析 | 计划摘要、元数据、范围预估 |

详见 [`docs/AI/EXECUTION_PLATFORM.md`](docs/AI/EXECUTION_PLATFORM.md)。

## 技术栈

- Python 3.12+
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
