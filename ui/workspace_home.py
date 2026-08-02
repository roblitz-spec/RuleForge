from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------------------
# Task card definitions
# ---------------------------------------------------------------------------

_TASK_DEFS: list[dict] = [
    {"id": "rename_files",   "icon": "📝", "title": "Rename Files",
     "desc": "Clean up a folder with consistent naming rules"},
    {"id": "organize_photos", "icon": "📷", "title": "Organize Photos",
     "desc": "Apply date-based naming to your photo collection"},
    {"id": "organize_downloads", "icon": "📥", "title": "Organize Downloads",
     "desc": "Standardize names in your Downloads folder"},
    {"id": "continue_previous", "icon": "📂", "title": "Continue Previous Work",
     "desc": "Reopen your most recent task or rule set"},
]


class _TaskCard(QFrame):
    """A single task entry on the Workspace home page."""

    clicked = Signal(str)

    def __init__(self, task_id: str, icon: str, title: str,
                 desc: str) -> None:
        super().__init__()
        self._task_id = task_id
        self.setObjectName("taskCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._base_style = (
            "#taskCard {"
            "  background: #fff;"
            "  border: 1px solid #e0e0e0;"
            "  border-radius: 8px;"
            "  padding: 20px;"
            "}"
            "#taskCard:hover {"
            "  border-color: #1a73e8;"
            "  background: #f8fbff;"
            "}"
        )
        self.setStyleSheet(self._base_style)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self._icon_label = QLabel(icon)
        self._icon_label.setStyleSheet("font-size: 28px;")
        layout.addWidget(self._icon_label)

        self._title_label = QLabel(title)
        self._title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #333;"
        )
        layout.addWidget(self._title_label)

        self._desc_label = QLabel(desc)
        self._desc_label.setWordWrap(True)
        self._desc_label.setStyleSheet("font-size: 11px; color: #777;")
        layout.addWidget(self._desc_label)

    def update_desc(self, text: str) -> None:
        self._desc_label.setText(text)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        self.clicked.emit(self._task_id)
        super().mousePressEvent(event)


class WorkspaceHome(QWidget):
    """Task-first landing page — "What would you like to do today?"

    Displays task cards and (when available) recent activity context.
    """

    task_selected = Signal(str, str)  # task_id, task_title

    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet("background: #f5f7fa;")

        self._outer = QVBoxLayout(self)
        self._outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # -- Recent activity section (hidden until set) --
        self._recent_section = QWidget()
        self._recent_section.setStyleSheet("background: transparent;")
        recent_layout = QVBoxLayout(self._recent_section)
        recent_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        recent_layout.setSpacing(8)

        self._recent_heading = QLabel("")
        self._recent_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._recent_heading.setStyleSheet(
            "font-size: 13px; color: #888; background: transparent;"
        )
        recent_layout.addWidget(self._recent_heading)

        self._recent_buttons_layout = QVBoxLayout()
        self._recent_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._recent_buttons_layout.setSpacing(6)
        recent_layout.addLayout(self._recent_buttons_layout)

        self._recent_section.hide()
        self._outer.addWidget(self._recent_section)

        # -- Heading --
        heading = QLabel("What would you like to do today?")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #333; "
            "padding: 0 0 32px 0; background: transparent;"
        )
        self._outer.addWidget(heading)

        # -- Task card grid (2×2) --
        grid = QWidget()
        grid.setStyleSheet("background: transparent;")
        grid_layout = QHBoxLayout(grid)
        grid_layout.setSpacing(16)

        col1 = QVBoxLayout()
        col1.setSpacing(16)
        col2 = QVBoxLayout()
        col2.setSpacing(16)

        self._cards: dict[str, _TaskCard] = {}
        for i, td in enumerate(_TASK_DEFS):
            card = _TaskCard(
                task_id=td["id"], icon=td["icon"],
                title=td["title"], desc=td["desc"],
            )
            card.clicked.connect(
                lambda tid=td["id"], ttl=td["title"]:
                self.task_selected.emit(tid, ttl)
            )
            card.setFixedSize(280, 160)
            self._cards[td["id"]] = card
            (col1 if i % 2 == 0 else col2).addWidget(card)

        grid_layout.addLayout(col1)
        grid_layout.addLayout(col2)
        self._outer.addWidget(grid, alignment=Qt.AlignmentFlag.AlignCenter)

        # -- Footer hint --
        hint = QLabel("All tasks run locally.  Nothing leaves your computer.")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(
            "font-size: 11px; color: #aaa; padding: 32px 0 0 0; "
            "background: transparent;"
        )
        self._outer.addWidget(hint)

    # ------------------------------------------------------------------
    # Public — refreshed by WorkspaceWindow on each visit
    # ------------------------------------------------------------------

    def set_recent(self, last_task: str | None,
                   recent: list[tuple[str, str]]) -> None:
        """Update the recent activity section with clickable task buttons."""
        # Clear previous buttons
        while self._recent_buttons_layout.count():
            item = self._recent_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if last_task:
            self._recent_heading.setText("📌  Recent Activity")
            self._recent_section.show()

            for tid, title in recent:
                btn = QPushButton(f"📂  {title}")
                btn.setFlat(True)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(
                    "QPushButton {"
                    "  background: #fff;"
                    "  border: 1px solid #e0e0e0;"
                    "  border-radius: 4px;"
                    "  padding: 6px 16px;"
                    "  font-size: 12px; color: #333;"
                    "}"
                    "QPushButton:hover {"
                    "  background: #f0f4ff;"
                    "  border-color: #1a73e8;"
                    "}"
                )
                btn.clicked.connect(
                    lambda checked, t=tid, tl=title:
                    self.task_selected.emit(t, tl)
                )
                self._recent_buttons_layout.addWidget(btn)

            card = self._cards.get("continue_previous")
            if card:
                card.update_desc(f"Continue: {last_task}")
        else:
            self._recent_section.hide()

            card = self._cards.get("continue_previous")
            if card:
                card.update_desc(
                    "Reopen your most recent task or rule set")
