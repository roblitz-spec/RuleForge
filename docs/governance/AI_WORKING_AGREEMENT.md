# AI Working Agreement

_Governance document — applies to all AI agents collaborating on this
repository (OpenHands, ChatGPT, Claude, etc.)._

## Rules

### 1. Read PROJECT_IDENTITY.md First

Before any work: read [`PROJECT_IDENTITY.md`](../../PROJECT_IDENTITY.md).
It defines the project identity, architecture, principles, maintenance
policy, and canonical documentation.

### 2. Respect Maintenance Mode

The project is in Maintenance Mode.  Only these changes are allowed:
bug fixes, documentation improvements, CI/tooling maintenance,
dependency maintenance.

Do not propose or implement new capabilities, refactoring, or
contract-breaking changes.

### 3. Respect Baseline

- M11: Execution Platform — frozen
- M12-B: Plugin Framework — frozen
- M12-C…K: 9 Capability Plugins — frozen
- All contracts: frozen

Do not modify frozen modules except for bug fixes.

### 4. Facts vs. Recommendations

Clearly distinguish:

- **Facts** — what the codebase says, what tests verify, what docs state
- **Recommendations** — what could be done differently, what might be improved

Do not present recommendations as facts.  Do not present facts as
recommendations.

### 5. Verified / Not Verified Reporting

When reporting status:

- State what was verified and how
- State what was not verified — use the explicit label **Not Verified**
- Do not mark something as Completed if it was not directly confirmed

### 6. Single Source of Truth

When referencing a rule, principle, or contract:

- Link to the canonical source (see `PROJECT_IDENTITY.md` §5)
- Do not restate rules from memory — point to the document

### 7. No Speculative Completion

Do not assume that a referenced file exists, a link resolves, or a
test passes without checking.  Verify, then report.

### 8. Major Milestone Decision Rule

If work exceeds the Maintenance Policy bounds:

1. Identify the gap explicitly
2. Propose a **Major Milestone** (M13+) with scope and rationale
3. Wait for explicit approval — do not start implementation speculatively

A Major Milestone requires: problem statement, scope boundaries,
impact analysis on frozen contracts, and explicit acceptance criteria.

---

*This agreement applies to all AI collaborators.  It may be updated as
collaboration patterns evolve.*
