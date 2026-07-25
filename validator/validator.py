from __future__ import annotations

from models.enums import ItemType
from models.file_item import FileItem
from models.validation_result import ValidationResult

_FORBIDDEN_CHARS = set(r'<>:"/\|?*')

_WIN_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def check_legality(name: str) -> str:
    """检查名称合法性，返回错误消息（空字符串表示合法）。"""
    if not name or not name.strip():
        return "名称不能为空"
    if any(c in name for c in _FORBIDDEN_CHARS):
        return "包含非法字符"
    if name.rstrip() != name:
        return "名称不能以空格结尾"
    if name.rstrip(".") != name:
        return "名称不能以 . 结尾"
    if len(name) > 255:
        return "名称过长"
    if name.upper() in _WIN_RESERVED:
        return f"「{name}」是系统保留名称"
    return ""


class Validator:
    """重命名前校验 —— 只检查 preview_name 的合法性。"""

    @staticmethod
    def validate(items: list[FileItem]) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        seen: dict[str, int] = {}  # preview_name → 首次出现索引

        for item in items:
            if item.item_type == ItemType.DIRECTORY:
                results.append(ValidationResult(file_path=item.full_path, is_valid=True))
                continue

            name = item.preview_name
            if name is None or name.strip() == "":
                results.append(ValidationResult(
                    file_path=item.full_path, is_valid=False, message="名称不能为空",
                ))
                continue

            if any(c in name for c in _FORBIDDEN_CHARS):
                results.append(ValidationResult(
                    file_path=item.full_path, is_valid=False, message="包含非法字符",
                ))
                continue

            if len(name) > 255:
                results.append(ValidationResult(
                    file_path=item.full_path, is_valid=False, message="名称过长",
                ))
                continue

            if name in seen:
                results.append(ValidationResult(
                    file_path=item.full_path, is_valid=False, message="目标名称重复",
                ))
                results[seen[name]].is_valid = False
                results[seen[name]].message = "目标名称重复"
            else:
                seen[name] = len(results)
                results.append(ValidationResult(file_path=item.full_path, is_valid=True))

        return results
