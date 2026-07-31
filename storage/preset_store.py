from __future__ import annotations

import json
import secrets
from pathlib import Path

from models.preset import Preset
from models.rule import Rule
from models.rule_step import RuleStep

_CURRENT_VERSION = 1


class PresetStore:
    """Preset 持久化存储 — JSON 文件 CRUD，非运行时状态持有者。"""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._presets: list[Preset] = []
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._presets = self._load_from_disk()
        self._loaded = True

    def _load_from_disk(self) -> list[Preset]:
        if not self._path.is_file():
            return []

        data = json.loads(self._path.read_text(encoding="utf-8"))

        presets: list[Preset] = []
        for item in data.get("presets", []):
            rules: list[Rule] = []
            for r in item.get("rules", []):
                steps: list[RuleStep] = []
                for s in r.get("steps", []):
                    step = RuleStep(type=s["type"], parameters=s.get("parameters", {}))
                    if "id" in s:
                        step.id = s["id"]
                    steps.append(step)
                rules.append(Rule(
                    id=r["id"],
                    name=r["name"],
                    description=r.get("description", ""),
                    steps=steps,
                    pinned=r.get("pinned", False),
                ))
            presets.append(Preset(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                rules=rules,
                version=item.get("version", 1),
            ))
        return presets

    def _save_to_disk(self) -> None:
        data = {
            "version": _CURRENT_VERSION,
            "presets": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "version": p.version,
                    "rules": [
                        {
                            "id": r.id,
                            "name": r.name,
                            "description": r.description,
                            "pinned": r.pinned,
                            "steps": [
                                {"id": s.id, "type": s.type, "parameters": s.parameters}
                                for s in r.steps
                            ],
                        }
                        for r in p.rules
                    ],
                }
                for p in self._presets
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

    def save(self, preset: Preset) -> None:
        self._ensure_loaded()
        for i, p in enumerate(self._presets):
            if p.id == preset.id:
                self._presets[i] = preset
                self._save_to_disk()
                return
        self._presets.append(preset)
        self._save_to_disk()

    def load_all(self) -> list[Preset]:
        self._ensure_loaded()
        return list(self._presets)

    def delete(self, preset_id: str) -> None:
        self._ensure_loaded()
        self._presets = [p for p in self._presets if p.id != preset_id]
        self._save_to_disk()

    def rename(self, preset_id: str, new_name: str) -> None:
        self._ensure_loaded()
        for p in self._presets:
            if p.id == preset_id:
                p.name = new_name
                self._save_to_disk()
                return

    def _next_id(self) -> str:
        self._ensure_loaded()
        existing = {p.id for p in self._presets}
        idx = 1
        while f"preset_{idx}" in existing:
            idx += 1
        return f"preset_{idx}"
