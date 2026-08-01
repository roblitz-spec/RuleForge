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

RuleForge follows strict separation of concerns. See
[`docs/architecture/principles.md`](docs/architecture/principles.md) for the
unified architecture principles and
[`docs/architecture/overview.md`](docs/architecture/overview.md) for the full
architecture baseline.

### Where Should Your Feature Go?

Use this decision guide:

```
New feature required
    │
    ├── Is it a rule transformation (replace, insert, date, number, etc.)?
    │   → RuleEngine (engine/rule_engine.py) — add a new handler
    │
    ├── Is it an execution behavior (how tasks run)?
    │   → ExecutionEngine (engine/) — implement ExecutionEngine interface
    │
    ├── Is it a Plugin Framework change (how plugins are managed)?
    │   → Framework (plugins/plugin*.py) — M12-B is frozen, Enhancement Proposal required
    │
    ├── Can it be composed from existing capability plugins?
    │   → Composition — use existing plugins together at the caller level
    │       Examples:
    │       • Audit trail = EventPlugin.emit() + NotificationPlugin.notify()
    │       • Rate limiting = PolicyPlugin.evaluate() + SchedulerPlugin
    │       • Status monitoring = EventPlugin.subscribe() + NotificationPlugin.notify_all()
    │
    ├── Does it pass all Capability Acceptance Rules?
    │   → New Capability Plugin — implement Plugin ABC
    │       Must satisfy all 6 rules. See docs/architecture/adr/005-capability-acceptance-rules.md
    │
    └── None of the above?
        → Re-evaluate the feature scope
```

### Capability Acceptance Rules

New capability plugins are accepted only when they satisfy all of:

1. **Cannot be composed** from existing capabilities
2. **Owns a unique** lifecycle responsibility
3. **Has a stable** public contract
4. **No responsibility overlap** with existing plugins
5. **Cannot reasonably belong** to Engine / Framework / Rule layer
6. **Implements Plugin ABC only** — zero cross-plugin or engine/ imports

See [ADR-005](docs/architecture/adr/005-capability-acceptance-rules.md) for details.

### Capability Plugin Template

```python
from dataclasses import dataclass
from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


@dataclass(frozen=True)
class MyDomainObject:
    name: str
    # ... domain fields


@dataclass(frozen=True)
class MyResult:
    success: bool
    message: str = ""


class MyPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.myplugin",
            version="1.0.0",
            description="...",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def __init__(self):
        self._items: dict[str, MyDomainObject] = {}

    def on_activate(self, ctx: PluginContext) -> None:
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        pass

    def register(self, obj: MyDomainObject) -> None:
        if obj.name in self._items:
            raise ValueError(f"'{obj.name}' already registered")
        self._items[obj.name] = obj

    def unregister(self, name: str) -> bool:
        return self._items.pop(name, None) is not None

    def list_all(self) -> tuple[MyDomainObject, ...]:
        return tuple(self._items.values())

    def get(self, name: str) -> MyDomainObject | None:
        return self._items.get(name)

    @property
    def item_count(self) -> int:
        return len(self._items)
```

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
