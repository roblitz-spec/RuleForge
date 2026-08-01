# Architecture Change Checklist

_For any change that might impact architecture, contracts, or the plugin
system.  Complete before proposing a Major Milestone._

## Checklist

### 1. Problem Statement

- [ ] What problem does this change solve?
- [ ] Why can't this be solved within the current architecture?

### 2. Existing Capability Evaluation

- [ ] Can this be achieved by composing existing plugins?
- [ ] Can this be achieved within an existing engine?
- [ ] Has `docs/ideas/ideas.md` been checked for prior evaluation?

### 3. Public Contract Impact

- [ ] Which frozen contracts would be affected?
- [ ] Is any public API signature changed?
- [ ] Is any ExecutionResult field changed?
- [ ] Is any PluginContext field changed?

### 4. Plugin Boundary Impact

- [ ] Would any existing plugin need modification?
- [ ] Would cross-plugin imports be introduced? (Prohibited — ADR-004)
- [ ] Would the Plugin ABC change?

### 5. ADR Required?

- [ ] Is this a new architectural decision? → ADR required
- [ ] Does it modify a prior ADR? → ADR required (with supersession)
- [ ] Is it purely additive with no architectural impact? → No ADR required

### 6. Documentation Required?

- [ ] `docs/architecture/overview.md` — if architecture layers change
- [ ] `docs/architecture/capability-matrix.md` — if capability set changes
- [ ] `docs/architecture/boundary-matrix.md` — if responsibility boundaries change
- [ ] `docs/architecture/capability-handbook.md` — if plugin API changes
- [ ] `CHANGELOG.md` — always for milestone changes
- [ ] `PROJECT_IDENTITY.md` — if project status or principles change

### 7. Major Milestone Required?

- [ ] Does this exceed Maintenance Policy bounds? → Major Milestone required
- [ ] Is a new M13+ milestone needed?
- [ ] Has scope been defined?
- [ ] Has explicit acceptance criteria been written?

### 8. Risks

- [ ] Backward compatibility risk?
- [ ] Test regression risk?
- [ ] Cross-plugin interaction risk?
- [ ] Documentation inconsistency risk?

### 9. Alternatives

- [ ] What alternatives were considered?
- [ ] Why was this approach chosen over alternatives?

---

*This checklist does not explain architecture.  See
[`docs/architecture/overview.md`](../architecture/overview.md) for architecture.
See [`docs/architecture/adr/`](../architecture/adr/) for past decisions.*
