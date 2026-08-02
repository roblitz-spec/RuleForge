from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class _FeatureCard(QFrame):
    """A planned-feature indicator — not an active control."""

    def __init__(self, icon: str, title: str, desc: str) -> None:
        super().__init__()
        self.setStyleSheet(
            "_FeatureCard {"
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

        text = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #555;")
        text.addWidget(title_label)
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 11px; color: #999;")
        text.addWidget(desc_label)
        layout.addLayout(text, stretch=1)

        badge = QLabel("planned")
        badge.setStyleSheet(
            "font-size: 9px; color: #aaa; border: 1px solid #ddd; "
            "border-radius: 4px; padding: 2px 6px;"
        )
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop)


class RuleStudioApp(QWidget):
    """Rule Studio — dedicated rule management workspace.

    Foundation stage: surfaces existing rule browsing/management alongside
    planned future capabilities.
    """

    open_rule_manager_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QLabel("Rule Studio")
        header.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333;"
        )
        layout.addWidget(header)

        desc = QLabel(
            "Create, test, and manage reusable renaming rules.  "
            "Rules authored here can be used across all Workspace applications."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(desc)

        # ------------------------------------------------------------------
        # Available: Rule Manager
        # ------------------------------------------------------------------
        section_label = QLabel("Available")
        section_label.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #333; "
            "padding-top: 8px;"
        )
        layout.addWidget(section_label)

        available = QFrame()
        available.setStyleSheet(
            "QFrame { background: #fff; border: 1px solid #e0e0e0; "
            "border-radius: 8px; padding: 16px; }"
        )
        avail_layout = QVBoxLayout(available)
        avail_layout.setSpacing(8)

        avail_title = QLabel("🔧  Rule Manager")
        avail_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        avail_layout.addWidget(avail_title)

        avail_desc = QLabel(
            "Browse, create, edit, duplicate, and delete rules.  "
            "All existing rule management functionality is available here."
        )
        avail_desc.setWordWrap(True)
        avail_desc.setStyleSheet("font-size: 11px; color: #666;")
        avail_layout.addWidget(avail_desc)

        open_mgr_btn = QPushButton("Open Rule Manager")
        open_mgr_btn.setStyleSheet(
            "QPushButton { background: #1a73e8; color: #fff; border: none; "
            "border-radius: 4px; padding: 8px 16px; font-size: 12px; }"
            "QPushButton:hover { background: #1557b0; }"
        )
        open_mgr_btn.clicked.connect(self.open_rule_manager_requested.emit)
        avail_layout.addWidget(open_mgr_btn)

        layout.addWidget(available)

        # ------------------------------------------------------------------
        # Planned: Future capabilities
        # ------------------------------------------------------------------
        section_label2 = QLabel("Planned")
        section_label2.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #333; "
            "padding-top: 16px;"
        )
        layout.addWidget(section_label2)

        features = [
            ("🧪", "Rule Testing",
             "Test rules against sample filenames before applying them."),
            ("✅", "Rule Validation",
             "Check rules for errors, missing parameters, and conflicts."),
            ("📤", "Rule Sharing",
             "Export and import rules to share with other users."),
            ("🤖", "AI-Assisted Authoring",
             "Let RuleForge suggest rules based on example transformations."),
        ]
        for icon, title, fdesc in features:
            layout.addWidget(_FeatureCard(icon, title, fdesc))

        layout.addStretch()
