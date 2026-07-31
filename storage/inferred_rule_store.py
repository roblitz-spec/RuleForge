"""InferredRuleStore — JSON persistence for inferred rules.

Follows PresetStore pattern: lazy-loaded, atomic write via temp file.
Stored at ~/.resourcehub/inferred_rules.json.
"""
from __future__ import annotations

import json
import secrets
from pathlib import Path

from models.inferred_rule import InferredRule
from models.rule import Rule
from models.rule_lifecycle import RuleLifecycle
from models.rule_step import RuleStep

_CURRENT_VERSION = 1


class InferredRuleStore:
    """Persistent storage for inferred rules — JSON file CRUD."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._rules: list[InferredRule] = []
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._rules = self._load_from_disk()
        self._loaded = True

    def _load_from_disk(self) -> list[InferredRule]:
        if not self._path.is_file():
            return []

        data = json.loads(self._path.read_text(encoding="utf-8"))
        rules: list[InferredRule] = []
        for item in data.get("rules", []):
            r_data = item["rule"]
            steps = [
                RuleStep(
                    type=s["type"],
                    parameters=s.get("parameters", {}),
                    id=s.get("id", str(__import__("uuid").uuid4())),
                )
                for s in r_data.get("steps", [])
            ]
            rule = Rule(
                id=r_data["id"],
                name=r_data["name"],
                description=r_data.get("description", ""),
                steps=steps,
                pinned=r_data.get("pinned", False),
            )
            lifecycle_raw = item.get("lifecycle", "INFERRED")
            lifecycle = RuleLifecycle[lifecycle_raw] if lifecycle_raw in RuleLifecycle.__members__ else RuleLifecycle.INFERRED
            rules.append(InferredRule(
                id=item["id"],
                rule=rule,
                source_examples=[(e[0], e[1]) for e in item.get("source_examples", [])],
                created_at=item.get("created_at", 0.0),
                lifecycle=lifecycle,
            ))
        return rules

    def _save_to_disk(self) -> None:
        data = {
            "version": _CURRENT_VERSION,
            "rules": [
                {
                    "id": r.id,
                    "rule": {
                        "id": r.rule.id,
                        "name": r.rule.name,
                        "description": r.rule.description,
                        "pinned": r.rule.pinned,
                        "steps": [
                            {"id": s.id, "type": s.type, "parameters": s.parameters}
                            for s in r.rule.steps
                        ],
                    },
                    "source_examples": list(r.source_examples),
                    "created_at": r.created_at,
                    "lifecycle": r.lifecycle.name,
                }
                for r in self._rules
            ],
        }
        tmp = self._path.with_suffix(f".tmp.{secrets.token_hex(6)}")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=4, default=str),
            encoding="utf-8",
        )
        tmp.replace(self._path)

    # ── CRUD ──────────────────────────────────────────────

    def save(self, rule: InferredRule) -> None:
        self._ensure_loaded()
        for i, r in enumerate(self._rules):
            if r.id == rule.id:
                self._rules[i] = rule
                self._save_to_disk()
                return
        self._rules.append(rule)
        self._save_to_disk()

    def load_all(self) -> list[InferredRule]:
        self._ensure_loaded()
        return list(self._rules)

    def delete(self, rule_id: str) -> None:
        self._ensure_loaded()
        self._rules = [r for r in self._rules if r.id != rule_id]
        self._save_to_disk()
