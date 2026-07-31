from __future__ import annotations

from copy import deepcopy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from editor.edit_session import EditSession
from models.preset import Preset
from storage.preset_store import PresetStore
from storage.repository import RuleRepository


class PresetManagerDialog(QDialog):
    """预设管理对话框 —— 保存 / 加载 / 删除 / 重命名预设。"""

    def __init__(
        self,
        repo: RuleRepository,
        preset_store: PresetStore,
        edit_session: EditSession | None = None,
        parent: QDialog | None = None,
    ) -> None:
        super().__init__(parent)
        self._repo = repo
        self._store = preset_store
        self._edit_session = edit_session

        self.setWindowTitle("预设管理")
        self.resize(500, 400)

        root = QHBoxLayout(self)

        # ── 左侧：预设列表 ──
        left = QVBoxLayout()
        left.addWidget(QLabel("已保存的预设"))
        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._on_load)
        self._list.currentItemChanged.connect(self._on_selection_changed)
        left.addWidget(self._list)

        # ── 右侧：操作按钮 ──
        right = QVBoxLayout()
        self._load_btn = QPushButton("加载")
        self._load_btn.clicked.connect(self._on_load)
        self._load_btn.setEnabled(False)
        right.addWidget(self._load_btn)

        self._save_btn = QPushButton("保存当前规则为预设…")
        self._save_btn.clicked.connect(self._on_save)
        right.addWidget(self._save_btn)

        self._delete_btn = QPushButton("删除")
        self._delete_btn.clicked.connect(self._on_delete)
        self._delete_btn.setEnabled(False)
        right.addWidget(self._delete_btn)

        self._rename_btn = QPushButton("重命名")
        self._rename_btn.clicked.connect(self._on_rename)
        self._rename_btn.setEnabled(False)
        right.addWidget(self._rename_btn)

        right.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        right.addWidget(close_btn)

        root.addLayout(left)
        root.addLayout(right)

        self._refresh_list()

    # ── Internal ──────────────────────────────────────────

    def _refresh_list(self) -> None:
        self._list.clear()
        for p in self._store.load_all():
            item = QListWidgetItem(
                f"{p.name}  （{len(p.rules)} 条规则）"
            )
            item.setData(Qt.UserRole, p.id)
            self._list.addItem(item)

        if self._list.count() == 0:
            empty = QListWidgetItem("（暂无已保存的预设）")
            empty.setFlags(Qt.NoItemFlags)
            self._list.addItem(empty)

    def _selected_id(self) -> str | None:
        item = self._list.currentItem()
        if item is None or item.flags() == Qt.NoItemFlags:
            return None
        return item.data(Qt.UserRole)

    # ── Actions ───────────────────────────────────────────

    def _on_selection_changed(self) -> None:
        has = self._selected_id() is not None
        self._load_btn.setEnabled(has)
        self._delete_btn.setEnabled(has)
        self._rename_btn.setEnabled(has)

    def _on_load(self) -> None:
        preset_id = self._selected_id()
        if preset_id is None:
            return

        # dirty session guard
        if self._edit_session is not None and self._edit_session.is_dirty():
            reply = QMessageBox.question(
                self, "未保存的更改",
                "当前有未保存的规则编辑，加载预设将丢失这些更改。\n\n确定要继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        presets = {p.id: p for p in self._store.load_all()}
        preset = presets.get(preset_id)
        if preset is None:
            return

        self._repo.replace_rules(deepcopy(preset.rules))
        self._repo.save()

        # discard active session if any
        if self._edit_session is not None:
            self._edit_session.discard()

        QMessageBox.information(self, "加载完成", f"已加载预设「{preset.name}」。")

    def _on_save(self) -> None:
        name, ok = QInputDialog.getText(
            self, "保存预设", "请输入预设名称：",
        )
        if not ok or not name.strip():
            return

        name = name.strip()

        # check if overwriting existing preset by name
        by_name = {p.name: p for p in self._store.load_all()}
        if name in by_name:
            reply = QMessageBox.question(
                self, "确认覆盖",
                f"已存在同名预设「{name}」，是否覆盖？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            preset_id = by_name[name].id
        else:
            preset_id = self._store._next_id()

        preset = Preset(
            id=preset_id,
            name=name,
            rules=deepcopy(self._repo.all_rules()),
        )
        self._store.save(preset)
        self._refresh_list()

    def _on_delete(self) -> None:
        preset_id = self._selected_id()
        if preset_id is None:
            return

        presets = {p.id: p for p in self._store.load_all()}
        preset = presets.get(preset_id)
        if preset is None:
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除预设「{preset.name}」吗？\n\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._store.delete(preset_id)
        self._refresh_list()

    def _on_rename(self) -> None:
        preset_id = self._selected_id()
        if preset_id is None:
            return

        presets = {p.id: p for p in self._store.load_all()}
        preset = presets.get(preset_id)
        if preset is None:
            return

        name, ok = QInputDialog.getText(
            self, "重命名预设", "请输入新名称：",
            text=preset.name,
        )
        if not ok or not name.strip():
            return

        self._store.rename(preset_id, name.strip())
        self._refresh_list()
