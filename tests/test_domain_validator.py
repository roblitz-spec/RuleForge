"""WP-2: DomainValidator — rule validation, step validation, parameter validation, result model."""
from __future__ import annotations

from editor.domain_validator import DomainValidator, ValidationIssue, ValidationSeverity
from models.rule import Rule
from models.rule_step import RuleStep


# ── Helpers ──

def _messages(issues: list[ValidationIssue]) -> list[str]:
    return [i.message for i in issues]


# ═══════════════════════════════════════════════════════════════════
# Validation Result Model
# ═══════════════════════════════════════════════════════════════════

class TestValidationResultModel:
    def test_issue_is_dataclass(self) -> None:
        issue = ValidationIssue(field="name", message="error")
        assert issue.field == "name"
        assert issue.message == "error"
        assert issue.severity == ValidationSeverity.ERROR

    def test_issue_severity_defaults_to_error(self) -> None:
        issue = ValidationIssue(field="x", message="y")
        assert issue.severity == ValidationSeverity.ERROR

    def test_severity_enum_values(self) -> None:
        assert ValidationSeverity.ERROR is not ValidationSeverity.WARNING


# ═══════════════════════════════════════════════════════════════════
# Rule-level Validation
# ═══════════════════════════════════════════════════════════════════

class TestRuleValidation:
    def test_valid_rule_no_errors(self) -> None:
        rule = Rule(id="r1", name="My Rule", steps=[])
        issues = DomainValidator.validate_rule(rule)
        assert issues == []

    def test_empty_name(self) -> None:
        rule = Rule(id="r1", name="", steps=[])
        issues = DomainValidator.validate_rule(rule)
        assert len(issues) == 1
        assert issues[0].field == "name"
        assert "不能为空" in issues[0].message

    def test_whitespace_name(self) -> None:
        rule = Rule(id="r1", name="   ", steps=[])
        issues = DomainValidator.validate_rule(rule)
        assert len(issues) == 1
        assert issues[0].field == "name"

    def test_duplicate_name(self) -> None:
        existing = [Rule(id="r2", name="My Rule")]
        rule = Rule(id="r1", name="My Rule")
        issues = DomainValidator.validate_rule(rule, existing_rules=existing)
        assert len(issues) == 1
        assert issues[0].field == "name"
        assert "已存在" in issues[0].message

    def test_same_name_same_id_not_duplicate(self) -> None:
        """Renaming a rule to its own current name is not a conflict."""
        existing = [Rule(id="r1", name="My Rule")]
        rule = Rule(id="r1", name="My Rule")
        issues = DomainValidator.validate_rule(rule, existing_rules=existing)
        assert issues == []

    def test_unique_name_no_errors(self) -> None:
        existing = [Rule(id="r2", name="Other")]
        rule = Rule(id="r1", name="My Rule")
        issues = DomainValidator.validate_rule(rule, existing_rules=existing)
        assert issues == []

    def test_no_uniqueness_check_when_no_existing(self) -> None:
        """Without existing_rules, uniqueness is not enforced."""
        rule = Rule(id="r1", name="Any Name")
        issues = DomainValidator.validate_rule(rule, existing_rules=None)
        assert issues == []

    def test_rule_validation_includes_step_errors(self) -> None:
        rule = Rule(
            id="r1",
            name="Valid Name",
            steps=[RuleStep(type="replace", parameters={"from": "", "to": "x"})],
        )
        issues = DomainValidator.validate_rule(rule)
        assert len(issues) == 1
        assert "from" in issues[0].field


# ═══════════════════════════════════════════════════════════════════
# Step-level Validation
# ═══════════════════════════════════════════════════════════════════

class TestStepValidation:
    def test_valid_replace_step(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "a", "to": "b"})
        assert DomainValidator.validate_step(step) == []

    def test_replace_from_empty(self) -> None:
        step = RuleStep(type="replace", parameters={"from": "", "to": "b"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1
        assert "from" in issues[0].field
        assert "from 不能为空" in issues[0].message

    def test_replace_from_missing(self) -> None:
        step = RuleStep(type="replace", parameters={"to": "b"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1

    def test_regex_pattern_empty(self) -> None:
        step = RuleStep(type="regex_replace", parameters={"pattern": "", "replacement": "x"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1
        assert "pattern" in issues[0].field

    def test_regex_pattern_missing(self) -> None:
        step = RuleStep(type="regex_replace", parameters={"replacement": "x"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1

    def test_number_valid(self) -> None:
        step = RuleStep(type="number", parameters={"start": "1", "step": "2", "padding": "3"})
        assert DomainValidator.validate_step(step) == []

    def test_number_step_zero(self) -> None:
        step = RuleStep(type="number", parameters={"step": "0"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1
        assert "step" in issues[0].field
        assert ">= 1" in issues[0].message

    def test_number_step_negative(self) -> None:
        step = RuleStep(type="number", parameters={"step": "-5"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1

    def test_number_step_not_int(self) -> None:
        step = RuleStep(type="number", parameters={"step": "abc"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1
        assert "有效数字" in issues[0].message

    def test_insert_valid(self) -> None:
        step = RuleStep(type="insert", parameters={"text": "x", "at_index": "5"})
        assert DomainValidator.validate_step(step) == []

    def test_insert_default_at_index(self) -> None:
        """Default at_index is 0, which is valid."""
        step = RuleStep(type="insert", parameters={"text": "x"})
        assert DomainValidator.validate_step(step) == []

    def test_insert_at_index_minus_2(self) -> None:
        step = RuleStep(type="insert", parameters={"at_index": "-2"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1
        assert "at_index" in issues[0].field

    def test_insert_at_index_minus_1_valid(self) -> None:
        """at_index = -1 is valid (clamps to end)."""
        step = RuleStep(type="insert", parameters={"at_index": "-1"})
        assert DomainValidator.validate_step(step) == []

    def test_insert_at_index_not_int(self) -> None:
        step = RuleStep(type="insert", parameters={"at_index": "xyz"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1
        assert "有效数字" in issues[0].message

    def test_date_valid(self) -> None:
        step = RuleStep(type="date", parameters={"format": "%Y-%m-%d"})
        assert DomainValidator.validate_step(step) == []

    def test_date_format_empty(self) -> None:
        step = RuleStep(type="date", parameters={"format": ""})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1
        assert "format" in issues[0].field

    def test_date_format_no_percent(self) -> None:
        step = RuleStep(type="date", parameters={"format": "YYYY-MM-DD"})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1

    def test_date_format_missing(self) -> None:
        step = RuleStep(type="date", parameters={})
        issues = DomainValidator.validate_step(step)
        assert len(issues) == 1

    def test_other_types_always_valid(self) -> None:
        for tp in ["case", "trim", "add_prefix", "add_suffix", "remove_text"]:
            step = RuleStep(type=tp, parameters={})
            assert DomainValidator.validate_step(step) == [], f"{tp} should be valid"


# ═══════════════════════════════════════════════════════════════════
# Existing Behavior Preservation
# ═══════════════════════════════════════════════════════════════════

class TestBehaviorPreservation:
    """DomainValidator must produce the same messages as RuleManagerDialog._validate()."""

    def test_same_error_messages_as_ui_validate(self) -> None:
        """Side-by-side: every error condition produces the identical message."""
        expected_messages = {
            "name_empty": "规则名称不能为空。",
            "name_duplicate": "规则名称「Test」已存在。",
            "replace_from": "Replace 步骤的 from 不能为空。",
            "regex_pattern": "Regex Replace 步骤的 pattern 不能为空。",
            "number_step_low": "Number 步骤的 step 必须 >= 1。",
            "number_step_bad": "Number 步骤的 step 不是有效数字。",
            "insert_at_index_low": "Insert 步骤的 at_index 必须 >= -1。",
            "insert_at_index_bad": "Insert 步骤的 at_index 不是有效数字。",
            "date_format": "Date 步骤的 format 必须包含有效的 strftime 格式（例如 %Y-%m-%d）。",
        }

        # Name empty
        issues = DomainValidator.validate_rule(Rule(id="r1", name=""))
        assert issues[0].message == expected_messages["name_empty"]

        # Name duplicate
        issues = DomainValidator.validate_rule(
            Rule(id="r1", name="Test"),
            existing_rules=[Rule(id="r2", name="Test")],
        )
        assert issues[0].message == expected_messages["name_duplicate"]

        # Replace from
        issues = DomainValidator.validate_step(
            RuleStep(type="replace", parameters={"from": ""}),
        )
        assert issues[0].message == expected_messages["replace_from"]

        # Regex pattern
        issues = DomainValidator.validate_step(
            RuleStep(type="regex_replace", parameters={"pattern": ""}),
        )
        assert issues[0].message == expected_messages["regex_pattern"]

        # Number step < 1
        issues = DomainValidator.validate_step(
            RuleStep(type="number", parameters={"step": "0"}),
        )
        assert issues[0].message == expected_messages["number_step_low"]

        # Number step invalid
        issues = DomainValidator.validate_step(
            RuleStep(type="number", parameters={"step": "abc"}),
        )
        assert issues[0].message == expected_messages["number_step_bad"]

        # Insert at_index < -1
        issues = DomainValidator.validate_step(
            RuleStep(type="insert", parameters={"at_index": "-5"}),
        )
        assert issues[0].message == expected_messages["insert_at_index_low"]

        # Insert at_index invalid
        issues = DomainValidator.validate_step(
            RuleStep(type="insert", parameters={"at_index": "xyz"}),
        )
        assert issues[0].message == expected_messages["insert_at_index_bad"]

        # Date format
        issues = DomainValidator.validate_step(
            RuleStep(type="date", parameters={"format": ""}),
        )
        assert issues[0].message == expected_messages["date_format"]
