from __future__ import annotations

import tempfile
from pathlib import Path

from engine.operation_logger import OperationLogger
from engine.preview_engine import PreviewEngine
from engine.rename_engine import RenameEngine
from engine.rename_plan_engine import RenamePlanEngine
from engine.undo_engine import UndoEngine
from models.enums import ItemType
from models.file_item import FileItem
from models.rename_policy import RenamePolicy
from models.rule import Rule
from models.rule_step import RuleStep
from scanner.scanner import Scanner
from validator.validator import Validator


class TestRenameE2E:
    """端到端重命名回归测试。"""

    def test_selection_aware_rename(self) -> None:
        """验证：选择单个文件 → 只 rename 该文件，不影响其他文件。"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "A.txt").write_text("A")
            (root / "B.txt").write_text("B")

            items = Scanner.scan([root])
            assert len(items) == 2

            # 只选 A.txt (index 0)
            rule = Rule(id="r", name="r", steps=[
                RuleStep(type="replace", parameters={"from": "A", "to": "X"}),
            ])

            # 模拟 selection: only process items[0]
            selected_items = [items[0]]
            PreviewEngine.generate_preview(selected_items, rule)
            assert selected_items[0].preview_name == "X"

            plans = RenamePlanEngine.generate(selected_items)
            results = RenameEngine.rename(plans)

            # A.txt → X.txt
            assert not (root / "A.txt").exists()
            assert (root / "X.txt").exists()

            # B.txt 未被改名
            assert (root / "B.txt").exists()
            assert (root / "B.txt").read_text() == "B"

    def test_single_file_replace_a_to_b(self) -> None:
        """A.txt → Replace A→B → B.txt"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "A.txt").write_text("hello")

            # 扫描
            items = Scanner.scan([root])
            assert len(items) == 1
            assert items[0].original_name == "A.txt"

            # 预览
            rule = Rule(id="r", name="r", steps=[
                RuleStep(type="replace", parameters={"from": "A", "to": "B"}),
            ])
            PreviewEngine.generate_preview(items, rule)
            assert items[0].preview_name == "B"

            # 校验
            results = Validator.validate(items)
            assert all(r.is_valid for r in results)

            # 执行
            rename_results = RenameEngine.rename(RenamePlanEngine.generate(items))
            assert rename_results[0].success
            assert not (root / "A.txt").exists()
            assert (root / "B.txt").exists()
            assert (root / "B.txt").read_text() == "hello"

    def test_full_cycle_scan_preview_rename_undo(self) -> None:
        """Scan → Preview → Rename → Undo 完整周期。"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "photo_001.jpg").write_text("p1")
            (root / "photo_002.jpg").write_text("p2")
            (root / "photo_003.jpg").write_text("p3")

            items = Scanner.scan([root])
            assert len(items) == 3

            rule = Rule(id="r", name="r", steps=[
                RuleStep(type="replace", parameters={"from": "photo", "to": "image"}),
            ])
            PreviewEngine.generate_preview(items, rule)
            for item in items:
                assert item.preview_name is not None
                assert item.preview_name.startswith("image_")

            logger = OperationLogger()
            plans = RenamePlanEngine.generate(items)
            rename_results = RenameEngine.rename(plans, logger=logger)
            assert all(r.success for r in rename_results)
            assert all(not (root / f"photo_00{i}.jpg").exists() for i in range(1, 4))
            assert all((root / f"image_00{i}.jpg").exists() for i in range(1, 4))

            undo_results = UndoEngine.undo(logger)
            assert len(undo_results) == 3
            assert all(r.success for r in undo_results)
            assert all((root / f"photo_00{i}.jpg").exists() for i in range(1, 4))
            assert all(not (root / f"image_00{i}.jpg").exists() for i in range(1, 4))

    def test_collision_skip_policy(self) -> None:
        """目标文件已存在 → SKIP 策略：跳过冲突，重命名非冲突文件。"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "A.txt").write_text("a")
            (root / "B.txt").write_text("b")
            (root / "X.txt").write_text("existing")  # 与 A→X 冲突

            items = Scanner.scan([root])
            assert len(items) == 3

            rule = Rule(id="r", name="r", steps=[
                RuleStep(type="replace", parameters={"from": "A", "to": "X"}),
                RuleStep(type="replace", parameters={"from": "B", "to": "Y"}),
            ])
            PreviewEngine.generate_preview(items, rule)

            plans = RenamePlanEngine.generate(items, policy=RenamePolicy.SKIP)
            RenameEngine.rename(plans)

            # A→X 冲突被跳过：A.txt 未被改名
            assert (root / "A.txt").exists()
            assert (root / "A.txt").read_text() == "a"
            # B→Y 成功
            assert not (root / "B.txt").exists()
            assert (root / "Y.txt").exists()
            # 原有 X.txt 未被覆盖
            assert (root / "X.txt").exists()
            assert (root / "X.txt").read_text() == "existing"

    def test_overwrite_policy(self) -> None:
        """目标文件已存在 → OVERWRITE 策略：覆盖已存在的文件。"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "A.txt").write_text("new_content")
            (root / "X.txt").write_text("old_content")

            items = Scanner.scan([root])
            rule = Rule(id="r", name="r", steps=[
                RuleStep(type="replace", parameters={"from": "A", "to": "X"}),
            ])
            PreviewEngine.generate_preview(items, rule)

            plans = RenamePlanEngine.generate(items, policy=RenamePolicy.OVERWRITE)
            results = RenameEngine.rename(plans)

            # A→X 覆盖
            a_result = [r for r in results if r.source.name == "A.txt"][0]
            assert a_result.success
            assert not (root / "A.txt").exists()
            assert (root / "X.txt").exists()
            assert (root / "X.txt").read_text() == "new_content"

    def test_case_only_rename_on_disk(self) -> None:
        """大小写重命名：A.txt → a.txt 在实际文件系统上执行。"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "A.txt").write_text("case_test")

            items = Scanner.scan([root])
            assert len(items) == 1

            rule = Rule(id="r", name="r", steps=[
                RuleStep(type="case", parameters={"mode": "lower"}),
            ])
            PreviewEngine.generate_preview(items, rule)
            assert items[0].preview_name == "a"

            plans = RenamePlanEngine.generate(items)
            results = RenameEngine.rename(plans)

            assert results[0].success
            # 大小写重命名后，原大写文件不再存在
            assert not (root / "A.txt").exists()
            # 新小写文件存在（Linux 大小写敏感，Windows 通过 samefile 处理）
            targets = list(root.iterdir())
            assert len(targets) == 1
            assert targets[0].read_text() == "case_test"
