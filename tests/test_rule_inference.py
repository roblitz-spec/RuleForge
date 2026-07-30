"""Tests for engine/rule_inference.py — Example → Rule Inference (M9)."""
from __future__ import annotations

from engine.rule_inference import infer_steps, validate_steps


# ── No Transformation ─────────────────────────────────────────────

class TestNoTransformation:
    def test_single_identical(self) -> None:
        assert infer_steps([("hello", "hello")]) == []

    def test_multiple_identical(self) -> None:
        assert infer_steps([("a", "a"), ("b", "b"), ("c", "c")]) == []

    def test_empty_pairs(self) -> None:
        assert infer_steps([]) == []


# ── Case Detection ────────────────────────────────────────────────

class TestCaseDetection:
    def test_upper_single(self) -> None:
        steps = infer_steps([("hello", "HELLO")])
        assert len(steps) == 1
        assert steps[0].type == "case"
        assert steps[0].parameters["mode"] == "upper"

    def test_upper_multiple(self) -> None:
        steps = infer_steps([("abc", "ABC"), ("def", "DEF"), ("ghi", "GHI")])
        assert len(steps) == 1
        assert steps[0].type == "case"
        assert steps[0].parameters["mode"] == "upper"

    def test_lower(self) -> None:
        steps = infer_steps([("HELLO", "hello"), ("WORLD", "world")])
        assert len(steps) == 1
        assert steps[0].type == "case"
        assert steps[0].parameters["mode"] == "lower"

    def test_title_multiword(self) -> None:
        pairs = [("hello world", "Hello World"), ("foo bar", "Foo Bar")]
        steps = infer_steps(pairs)
        assert len(steps) >= 1
        assert any(s.type == "case" and s.parameters.get("mode") == "title" for s in steps)
        assert validate_steps(pairs, steps)

    def test_capitalize_multiword(self) -> None:
        pairs = [("hello world", "Hello world"), ("foo bar", "Foo bar")]
        steps = infer_steps(pairs)
        assert len(steps) >= 1
        assert any(s.type == "case" and s.parameters.get("mode") == "capitalize" for s in steps)
        assert validate_steps(pairs, steps)

    def test_mixed_case_no_consensus(self) -> None:
        steps = infer_steps([("abc", "ABC"), ("DEF", "def")])
        case_steps = [s for s in steps if s.type == "case"]
        assert case_steps == []


# ── Trim Detection ────────────────────────────────────────────────

class TestTrimDetection:
    def test_strip_both(self) -> None:
        steps = infer_steps([("  hello  ", "hello"), ("  world  ", "world")])
        assert validate_steps([("  hello  ", "hello"), ("  world  ", "world")], steps)

    def test_strip_left(self) -> None:
        steps = infer_steps([("  hello", "hello"), ("  world", "world")])
        assert validate_steps([("  hello", "hello"), ("  world", "world")], steps)

    def test_strip_right(self) -> None:
        steps = infer_steps([("hello  ", "hello"), ("world  ", "world")])
        assert validate_steps([("hello  ", "hello"), ("world  ", "world")], steps)


# ── Replace Detection ─────────────────────────────────────────────

class TestReplaceDetection:
    def test_single_replace(self) -> None:
        pairs = [("hello world", "hello_earth"), ("hey world", "hey_earth")]
        steps = infer_steps(pairs)
        assert len(steps) >= 1
        assert validate_steps(pairs, steps)

    def test_remove_text(self) -> None:
        pairs = [("hello_abc", "hello"), ("world_abc", "world")]
        steps = infer_steps(pairs)
        assert len(steps) >= 1
        assert validate_steps(pairs, steps)

    def test_replace_space_with_underscore(self) -> None:
        steps = infer_steps([("hello world", "hello_world"), ("foo bar", "foo_bar")])
        replace = [s for s in steps if s.type == "replace"]
        assert len(replace) == 1
        assert replace[0].parameters["from"] == " "
        assert replace[0].parameters["to"] == "_"


# ── Prefix / Suffix Detection ─────────────────────────────────────

class TestPrefixDetection:
    def test_add_prefix(self) -> None:
        steps = infer_steps([("hello", "IMG_hello"), ("world", "IMG_world")])
        prefix = [s for s in steps if s.type == "add_prefix"]
        assert len(prefix) == 1
        assert prefix[0].parameters["text"] == "IMG_"

    def test_inconsistent_prefix_no_detection(self) -> None:
        steps = infer_steps([("hello", "A_hello"), ("world", "B_world")])
        prefix = [s for s in steps if s.type == "add_prefix"]
        assert prefix == []


class TestSuffixDetection:
    def test_add_suffix(self) -> None:
        steps = infer_steps([("hello", "hello_v1"), ("world", "world_v1")])
        suffix = [s for s in steps if s.type == "add_suffix"]
        assert len(suffix) == 1
        assert suffix[0].parameters["text"] == "_v1"

    def test_inconsistent_suffix_no_detection(self) -> None:
        steps = infer_steps([("hello", "hello_a"), ("world", "world_b")])
        suffix = [s for s in steps if s.type == "add_suffix"]
        assert suffix == []


# ── Multi-Step Pipelines ──────────────────────────────────────────

class TestMultiStepPipelines:
    def test_case_then_replace(self) -> None:
        pairs = [
            ("hello world", "HELLO_WORLD"),
            ("foo bar baz", "FOO_BAR_BAZ"),
        ]
        steps = infer_steps(pairs)
        assert len(steps) >= 1
        assert validate_steps(pairs, steps)

    def test_trim_then_case(self) -> None:
        pairs = [("  hello  ", "HELLO"), ("  world  ", "WORLD")]
        steps = infer_steps(pairs)
        assert len(steps) >= 1
        assert validate_steps(pairs, steps)

    def test_case_then_suffix(self) -> None:
        pairs = [("hello", "HELLO_v1"), ("world", "WORLD_v1")]
        steps = infer_steps(pairs)
        assert len(steps) >= 1
        assert validate_steps(pairs, steps)


# ── validate_steps ────────────────────────────────────────────────

class TestValidateSteps:
    def test_valid(self) -> None:
        from models.rule_step import RuleStep
        steps = [RuleStep(type="case", parameters={"mode": "upper"})]
        assert validate_steps([("hello", "HELLO"), ("world", "WORLD")], steps)

    def test_invalid(self) -> None:
        from models.rule_step import RuleStep
        steps = [RuleStep(type="case", parameters={"mode": "lower"})]
        assert not validate_steps([("HELLO", "hello"), ("WORLD", "WORLD")], steps)

    def test_empty_steps_identical_pairs(self) -> None:
        assert validate_steps([("a", "a"), ("b", "b")], [])

    def test_empty_steps_different_pairs(self) -> None:
        assert not validate_steps([("a", "b")], [])


# ── Edge Cases ────────────────────────────────────────────────────

class TestEdgeCases:
    def test_unicode(self) -> None:
        steps = infer_steps([("你好", "你好！"), ("世界", "世界！")])
        suffix = [s for s in steps if s.type == "add_suffix"]
        assert len(suffix) == 1
        assert suffix[0].parameters["text"] == "！"

    def test_single_example_sufficient(self) -> None:
        pairs = [("hello world", "HELLO_WORLD")]
        steps = infer_steps(pairs)
        assert len(steps) >= 1
        assert validate_steps(pairs, steps)

    def test_empty_strings(self) -> None:
        assert infer_steps([("", ""), ("", "")]) == []

    def test_empty_to_nonempty(self) -> None:
        steps = infer_steps([("", "prefix")])
        assert len(steps) >= 1
