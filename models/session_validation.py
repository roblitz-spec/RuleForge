"""Session-level validation results for RuleSession.

UI-independent — reusable by CLI, API, and GUI.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from editor.domain_validator import ValidationIssue


@dataclass
class SessionValidationResult:
    """Result of validating a Rule through RuleSession.validate().

    Combines domain-level validation (Rule/RuleStep checks from
    DomainValidator) with session-level checks (e.g. empty rule,
    lifecycle state).
    """

    is_valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    session_errors: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return len(self.issues) + len(self.session_errors)

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        self.is_valid = False

    def add_session_error(self, message: str) -> None:
        self.session_errors.append(message)
        self.is_valid = False

    def merge(self, other: SessionValidationResult) -> None:
        """Merge another result into this one."""
        self.issues.extend(other.issues)
        self.session_errors.extend(other.session_errors)
        if not other.is_valid:
            self.is_valid = False
