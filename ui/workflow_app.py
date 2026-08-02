from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class _PlannedCard(QFrame):
    """A planned-capability indicator — informational only, not interactive."""

    def __init__(self, icon: str, title: str, desc: str) -> None:
        super().__init__()
        self.setStyleSheet(
            "_PlannedCard {"
            "  background: #f9f9f9;"
            "  border: 1px dashed #ddd;"
            "  border-radius: 6px;"
            "  padding: 12px;"
            "}"
        )
        layout = QHBoxLayout(self)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #555;")
        text_layout.addWidget(title_label)
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 11px; color: #999;")
        text_layout.addWidget(desc_label)
        layout.addLayout(text_layout, stretch=1)

        badge = QLabel("planned")
        badge.setStyleSheet(
            "font-size: 9px; color: #aaa; border: 1px solid #ddd; "
            "border-radius: 4px; padding: 2px 6px;"
        )
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop)


class WorkflowApp(QWidget):
    """Workflow — future home for multi-step task composition.

    Foundation stage: establishes the product concept without introducing
    execution, persistence, scheduling, or orchestration.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QLabel("Workflow")
        header.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333;"
        )
        layout.addWidget(header)

        desc = QLabel(
            "Workflow will help you organize and automate multi-step "
            "renaming tasks.  Define a sequence — scan → apply rules → "
            "preview → execute — and run it reliably every time."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(desc)

        # ------------------------------------------------------------------
        # Available today
        # ------------------------------------------------------------------
        section = QLabel("Available Today")
        section.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #333; "
            "padding-top: 8px;"
        )
        layout.addWidget(section)

        today = QFrame()
        today.setStyleSheet(
            "QFrame { background: #fff; border: 1px solid #e0e0e0; "
            "border-radius: 8px; padding: 16px; }"
        )
        today_layout = QVBoxLayout(today)
        today_layout.setSpacing(8)

        today_title = QLabel("📋  Single-Task Workflow")
        today_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #333;")
        today_layout.addWidget(today_title)

        today_desc = QLabel(
            "You can already perform complete single-task workflows via "
            "ResourceHub: select a folder → configure rules → preview → "
            "execute.  Each step includes safety checks and rollback."
        )
        today_desc.setWordWrap(True)
        today_desc.setStyleSheet("font-size: 11px; color: #666;")
        today_layout.addWidget(today_desc)

        note = QLabel("Use ResourceHub to start a task now.")
        note.setStyleSheet(
            "font-size: 11px; color: #1a73e8; font-style: italic;")
        today_layout.addWidget(note)

        layout.addWidget(today)

        # ------------------------------------------------------------------
        # Planned capabilities
        # ------------------------------------------------------------------
        section2 = QLabel("Planned")
        section2.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #333; "
            "padding-top: 16px;"
        )
        layout.addWidget(section2)

        planned = [
            ("🔄", "Multi-Step Workflows",
             "Chain multiple rule sets and folders into a single automated sequence."),
            ("⏰", "Scheduled Execution",
             "Run recurring workflows on a timer or schedule."),
            ("🔗", "Workflow Templates",
             "Save and reuse common workflow patterns across projects."),
            ("📊", "Workflow History & Reports",
             "Review workflow execution history with detailed task reports."),
        ]
        for icon, title, pdesc in planned:
            layout.addWidget(_PlannedCard(icon, title, pdesc))

        layout.addStretch()
