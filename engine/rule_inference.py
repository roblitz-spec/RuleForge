"""RuleInference — derive RuleSteps from (original, desired) example pairs.

Pure function module.  No state, no UI, no filesystem access.

Core capability for M9: Example → Rule Inference.

Algorithm: combinatorial search over consensus candidates.
  1. Per pair, enumerate all single-step candidates (permissive).
  2. Intersect across all pairs to find consensus candidates.
  3. Search 1-step, 2-step, and 3-step combinations.
  4. Return the first valid pipeline.

Public API:
  - infer_steps(pairs) → list[RuleStep] — low-level, bare steps
  - infer_rule(pairs, name) → InferredRule | None — M10: full model
"""
from __future__ import annotations

from difflib import SequenceMatcher
from uuid import uuid4

from models.inferred_rule import InferredRule
from models.rule import Rule
from models.rule_step import RuleStep

_MAX_DEPTH = 3


# ── Per-Pair Candidate Generation ─────────────────────────────────

def _case_candidates(o: str, d: str) -> list[RuleStep]:
    """All case modes that change the string (permissive — search validates)."""
    if o == d:
        return []
    result: list[RuleStep] = []
    for mode, transform in [
        ("upper", str.upper), ("lower", str.lower),
        ("title", str.title), ("capitalize", str.capitalize),
    ]:
        if transform(o) != o:
            result.append(RuleStep(type="case", parameters={"mode": mode}))
    return result


def _trim_candidates(o: str, d: str) -> list[RuleStep]:
    """All trim modes that change the string (permissive)."""
    if o == d:
        return []
    result: list[RuleStep] = []
    for mode, transform in [
        ("both", str.strip), ("left", str.lstrip), ("right", str.rstrip),
    ]:
        if transform(o) != o:
            result.append(RuleStep(type="trim", parameters={"mode": mode}))
    return result


def _diff_candidates(o: str, d: str) -> list[RuleStep]:
    """Replace / remove / insert / affix candidates via SequenceMatcher diff."""
    if o == d:
        return []
    result: list[RuleStep] = []
    sm = SequenceMatcher(None, o, d)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace":
            result.append(RuleStep(
                type="replace",
                parameters={"from": o[i1:i2], "to": d[j1:j2]},
            ))
        elif tag == "delete":
            result.append(RuleStep(
                type="remove_text",
                parameters={"text": o[i1:i2]},
            ))
        elif tag == "insert":
            text = d[j1:j2]
            if i1 == 0:
                result.append(RuleStep(
                    type="add_prefix", parameters={"text": text},
                ))
            elif i1 >= len(o):
                result.append(RuleStep(
                    type="add_suffix", parameters={"text": text},
                ))
            else:
                result.append(RuleStep(
                    type="insert",
                    parameters={"text": text, "at_index": str(i1)},
                ))
    return result


def _affix_candidates(o: str, d: str) -> list[RuleStep]:
    """Prefix / suffix detection when d = text + o or d = o + text."""
    if o == d:
        return []
    result: list[RuleStep] = []
    if d.endswith(o) and len(d) > len(o):
        result.append(RuleStep(
            type="add_prefix",
            parameters={"text": d[:len(d) - len(o)]},
        ))
    if d.startswith(o) and len(d) > len(o):
        result.append(RuleStep(
            type="add_suffix",
            parameters={"text": d[len(o):]},
        ))
    return result


def _candidates_for_pair(o: str, d: str) -> list[RuleStep]:
    """All plausible single-step candidates for one (original, desired) pair."""
    candidates: list[RuleStep] = []
    candidates.extend(_case_candidates(o, d))
    candidates.extend(_trim_candidates(o, d))
    candidates.extend(_diff_candidates(o, d))
    candidates.extend(_affix_candidates(o, d))
    seen: set[tuple[str, str]] = set()
    unique: list[RuleStep] = []
    for s in candidates:
        key = (s.type, str(sorted(s.parameters.items())))
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


# ── Consensus Intersection ────────────────────────────────────────

def _step_key(step: RuleStep) -> tuple[str, tuple[tuple[str, str], ...]]:
    return (step.type, tuple(sorted(
        (str(k), str(v)) for k, v in step.parameters.items()
    )))


def _intersect_candidates(pairs: list[tuple[str, str]]) -> list[RuleStep]:
    """Find steps that appear in ALL pairs' candidate lists."""
    if not pairs:
        return []
    common: dict[tuple[str, tuple[tuple[str, str], ...]], RuleStep] = {}
    for i, (o, d) in enumerate(pairs):
        pair_candidates = _candidates_for_pair(o, d)
        pair_keys = {_step_key(s): s for s in pair_candidates}
        if i == 0:
            common = dict(pair_keys)
        else:
            common = {k: v for k, v in common.items() if k in pair_keys}
    return list(common.values())


# ── Search ────────────────────────────────────────────────────────

def _search(
    pairs: list[tuple[str, str]],
    candidates: list[RuleStep],
    depth: int,
) -> list[RuleStep] | None:
    if depth == 0:
        return None

    originals = [o for o, _ in pairs]
    desireds = [d for _, d in pairs]

    for step in candidates:
        applied = [_apply_step(o, step) for o in originals]
        if applied == originals:
            continue
        if all(a == d for a, d in zip(applied, desireds)):
            return [step]
        residual_pairs = list(zip(applied, desireds))
        residual_candidates = _intersect_candidates(residual_pairs)
        tail = _search(residual_pairs, residual_candidates, depth - 1)
        if tail is not None:
            return [step] + tail

    return None


# ── Public API ────────────────────────────────────────────────────

def infer_steps(pairs: list[tuple[str, str]]) -> list[RuleStep]:
    """Derive candidate RuleSteps from (original, desired) example pairs.

    Returns empty list if no transformation is needed or inference fails.
    """
    if not pairs:
        return []
    if all(o == d for o, d in pairs):
        return []

    candidates = _intersect_candidates(pairs)
    if not candidates:
        return []

    result = _search(pairs, candidates, _MAX_DEPTH)
    return result if result is not None else []


def _apply_step(text: str, step: RuleStep) -> str:
    """Apply a single RuleStep to text (subset of RuleEngine handlers)."""
    tp = step.type
    params = step.parameters

    if tp == "case":
        mode = str(params.get("mode", "lower"))
        if mode == "upper":
            return text.upper()
        elif mode == "lower":
            return text.lower()
        elif mode == "title":
            return text.title()
        elif mode == "capitalize":
            return text.capitalize()
    elif tp == "trim":
        mode = str(params.get("mode", "both"))
        if mode == "left":
            return text.lstrip()
        elif mode == "right":
            return text.rstrip()
        return text.strip()
    elif tp == "replace":
        return text.replace(str(params["from"]), str(params["to"]))
    elif tp == "remove_text":
        return text.replace(str(params["text"]), "")
    elif tp == "add_prefix":
        return str(params["text"]) + text
    elif tp == "add_suffix":
        return text + str(params["text"])
    elif tp == "insert":
        insert_text = str(params.get("text", ""))
        at_idx = int(str(params.get("at_index", "0")))
        if at_idx < 0 or at_idx > len(text):
            at_idx = len(text)
        return text[:at_idx] + insert_text + text[at_idx:]

    return text


def infer_rule(
    pairs: list[tuple[str, str]],
    name: str = "Inferred Rule",
) -> InferredRule | None:
    """Derive a complete InferredRule from example pairs.

    Args:
        pairs: List of (original_string, desired_output) examples.
        name: Human-readable name for the inferred rule.

    Returns:
        InferredRule if inference succeeds, None if no transformation
        is needed or inference fails.
    """
    steps = infer_steps(pairs)
    if not steps:
        return None

    rule = Rule(
        id=str(uuid4()),
        name=name,
        description=f"Inferred from {len(pairs)} example(s)",
        steps=steps,
    )
    return InferredRule(
        rule=rule,
        source_examples=list(pairs),
    )


def validate_steps(pairs: list[tuple[str, str]], steps: list[RuleStep]) -> bool:
    """Verify that applying *steps* in order correctly transforms every pair."""
    for original, desired in pairs:
        result = original
        for step in steps:
            result = _apply_step(result, step)
        if result != desired:
            return False
    return True
