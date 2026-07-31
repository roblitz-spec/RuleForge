# Contributing to RuleForge

Thanks for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/roblitz-spec/RuleForge.git
cd RuleForge
pip install -r requirements.txt
```

## Development Workflow

1. **Fork & Branch** — create a feature branch from `m11-execution-platform`
2. **Small Steps** — each commit should be a single logical change
3. **Tests** — add tests for new features, ensure all pass:
   ```bash
   python -m pytest tests/ -q
   ```
4. **Documentation** — update `AGENTS.md` and relevant docs for behavioral changes
5. **Pull Request** — target `m11-execution-platform`, describe what and why

## Branch Policy

- **Primary development branch**: `m11-execution-platform` — all PRs target this branch
- **`master`**: Legacy historical branch — not used for active development
- **Feature branches**: created from `m11-execution-platform`, merged back via PR

## Architecture Principles

RuleForge follows strict separation of concerns:

- **RuleEngine**: pure functions, stateless, driven by `context`
- **ExecutionPipeline**: coordinates execute lifecycle (validate → prepare → execute → cleanup)
- **ExecutionEngine**: implements behavior, never orchestration
- **EngineRegistry**: selects engines; Pipeline does NOT
- **BatchExecutor**: pure coordination — delegates to ExecutionPipeline

See [`docs/AI/EXECUTION_PLATFORM.md`](docs/AI/EXECUTION_PLATFORM.md) for the full architecture baseline.

## Code Style

- Python 3.13+, type hints on public APIs
- Minimal comments — code should be self-documenting
- Imports at top, organized: stdlib → third-party → local

## Commit Messages

```
Mxx: Brief description of change

Detailed body if needed.
```

## License

Apache 2.0. See [LICENSE](LICENSE).

---

*This contributing guide was created by an AI agent (OpenHands) on behalf of the project maintainer.*
