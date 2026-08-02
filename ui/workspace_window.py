from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from config.settings import Settings
from ui.main_window import MainWindow
from ui.history_app import HistoryApp
from ui.rule_studio_app import RuleStudioApp
from ui.workflow_app import WorkflowApp
from ui.workspace_home import WorkspaceHome

# ---------------------------------------------------------------------------
# Workspace Application Model
# ---------------------------------------------------------------------------


class AppStatus:
    ACTIVE = "active"
    COMING_SOON = "coming_soon"


@dataclass(frozen=True)
class WorkspaceApp:
    """A registered application within the RuleForge Workspace.

    Static registration only — no plugin loading or dynamic discovery.
    """

    app_id: str
    name: str
    icon: str
    description: str
    status: str  # AppStatus.ACTIVE | AppStatus.COMING_SOON

    @property
    def is_available(self) -> bool:
        return self.status == AppStatus.ACTIVE


# ---------------------------------------------------------------------------
# Registered applications
# ---------------------------------------------------------------------------

_APP_REGISTRY: list[WorkspaceApp] = [
    WorkspaceApp(
        app_id="resourcehub", name="ResourceHub", icon="📁",
        description="File renaming and organization",
        status=AppStatus.ACTIVE,
    ),
    WorkspaceApp(
        app_id="rule_studio", name="Rule Studio", icon="🔧",
        description="Rule authoring, testing, and sharing",
        status=AppStatus.ACTIVE,
    ),
    WorkspaceApp(
        app_id="workflow", name="Workflow", icon="📋",
        description="Multi-step task composition",
        status=AppStatus.ACTIVE,
    ),
    WorkspaceApp(
        app_id="history", name="History", icon="📜",
        description="Task and execution history browser",
        status=AppStatus.ACTIVE,
    ),
]


class _NavItem(QFrame):
    """A single navigation entry in the Workspace sidebar."""

    clicked = Signal(str)

    def __init__(self, app: WorkspaceApp) -> None:
        super().__init__()
        self._app = app
        self.setToolTip(app.description)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        icon_label = QLabel(app.icon)
        icon_label.setFixedWidth(24)
        layout.addWidget(icon_label)

        name_label = QLabel(app.name)
        name_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(name_label)

        if not app.is_available:
            badge = QLabel("soon")
            badge.setStyleSheet(
                "font-size: 9px; color: #999; "
                "border: 1px solid #ccc; border-radius: 4px; padding: 1px 5px;"
            )
            layout.addWidget(badge)
            self.setStyleSheet(
                "_NavItem { color: #999; }"
                "_NavItem:hover { background: #f5f5f5; }"
            )
        else:
            self.setStyleSheet(
                "_NavItem { background: #e8f0fe; border-left: 3px solid #1a73e8; "
                "font-weight: bold; }"
            )

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if self._app.is_available:
            self.clicked.emit(self._app.app_id)
        super().mousePressEvent(event)


class WorkspaceWindow(QMainWindow):
    """RuleForge Workspace — product entry point (M13.4).

    Task-first home, scalable navigation, application-container shell,
    session persistence, and working-workspace context.
    All runtime behavior is unchanged.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RuleForge Workspace")
        self.resize(1280, 720)
        self.setMinimumSize(1024, 640)

        self._settings = Settings()

        # --- Application registry lookup ---
        self._registry: dict[str, WorkspaceApp] = {
            a.app_id: a for a in _APP_REGISTRY
        }

        # ------------------------------------------------------------------
        # Central layout: sidebar | content (header + app host)
        # ------------------------------------------------------------------
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        nav = self._create_nav()
        root.addWidget(nav)

        # Right side: workspace header + application stack
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Workspace context header
        self._ws_header = self._create_ws_header()
        right_layout.addWidget(self._ws_header)

        # Application host
        self._app_stack = QStackedWidget()
        right_layout.addWidget(self._app_stack, stretch=1)

        # --- Mount pages ---
        self._apps: dict[str, QWidget] = {}
        self._active_app_id: str = ""

        # Home page (task-first landing)
        self._home = WorkspaceHome()
        self._home.task_selected.connect(self._on_task_selected)
        self._register_app("home", self._home)

        # ResourceHub
        self._resourcehub = MainWindow()
        self._register_app("resourcehub", self._resourcehub)

        # History — shares MainWindow's OperationLogger
        self._history = HistoryApp(self._resourcehub._logger)
        self._register_app("history", self._history)

        # Rule Studio — signal-based decoupling from MainWindow internals
        self._rule_studio = RuleStudioApp()
        self._rule_studio.open_rule_manager_requested.connect(
            self._resourcehub.open_rule_manager)
        self._register_app("rule_studio", self._rule_studio)

        # Workflow — product concept foundation, no execution
        self._workflow = WorkflowApp()
        self._register_app("workflow", self._workflow)

        root.addWidget(right, stretch=1)

        # --- Status bar ---
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Workspace ready")

        # --- Session state (in-memory, persisted via Settings) ---
        self._last_task_title: str | None = None
        self._recent_tasks: list[tuple[str, str]] = []  # [(task_id, title)]

        # --- Load persisted workspace session ---
        last_app = self._restore_session()

        # --- Restore last active application, or start on home ---
        if last_app and last_app in self._apps:
            self._activate_app(last_app)
        else:
            self._activate_app("home")

    # ------------------------------------------------------------------
    # Navigation sidebar
    # ------------------------------------------------------------------

    def _create_nav(self) -> QWidget:
        nav = QWidget()
        nav.setObjectName("workspaceNav")
        nav.setFixedWidth(220)
        nav.setStyleSheet(
            "#workspaceNav { background: #fafafa; border-right: 1px solid #e0e0e0; }"
        )
        layout = QVBoxLayout(nav)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(0)

        # Workspace brand (clickable → home)
        brand = QLabel("RuleForge")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333; padding: 8px 0 12px 0;"
        )
        brand.setCursor(Qt.CursorShape.PointingHandCursor)
        brand.mousePressEvent = lambda e: self._activate_app("home")  # type: ignore[assignment]
        layout.addWidget(brand)

        # Section label
        section = QLabel("  APPLICATIONS")
        section.setStyleSheet(
            "font-size: 10px; color: #999; letter-spacing: 1px; "
            "padding: 8px 12px 4px 12px;"
        )
        layout.addWidget(section)

        # Navigation items — driven by _APP_REGISTRY
        self._nav_items: dict[str, _NavItem] = {}
        for app in _APP_REGISTRY:
            item = _NavItem(app)
            item.clicked.connect(self._on_nav_clicked)
            self._nav_items[app.app_id] = item
            layout.addWidget(item)

        layout.addStretch()

        # Footer
        footer = QLabel("M13.4 · Working Workspace")
        footer.setStyleSheet("font-size: 10px; color: #bbb; padding: 8px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        return nav

    # ------------------------------------------------------------------
    # Workspace context header
    # ------------------------------------------------------------------

    def _create_ws_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(40)
        header.setStyleSheet(
            "background: #fff; border-bottom: 1px solid #e0e0e0;"
        )
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # Home button (visible when not on home page)
        self._home_btn = QPushButton("⌂ Home")
        self._home_btn.setFlat(True)
        self._home_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._home_btn.setStyleSheet(
            "font-size: 11px; color: #1a73e8; border: none; padding: 2px 6px;"
        )
        self._home_btn.clicked.connect(lambda: self._activate_app("home"))
        self._home_btn.hide()
        layout.addWidget(self._home_btn)

        self._active_label = QLabel("")
        self._active_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #333;"
        )
        layout.addWidget(self._active_label)

        layout.addStretch()

        self._context_label = QLabel("")
        self._context_label.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(self._context_label)

        return header

    # ------------------------------------------------------------------
    # Application management
    # ------------------------------------------------------------------

    def _register_app(self, app_id: str, widget: QWidget) -> None:
        self._apps[app_id] = widget
        self._app_stack.addWidget(widget)

    def _activate_app(self, app_id: str) -> None:
        if app_id not in self._apps:
            return
        self._active_app_id = app_id
        widget = self._apps[app_id]
        self._app_stack.setCurrentWidget(widget)

        if app_id == "home":
            self._active_label.setText("")
            self._context_label.setText("")
            self._home_btn.hide()
            self.setWindowTitle("RuleForge Workspace")
            self.statusBar().showMessage("What would you like to do today?")
            # Refresh recent activity on each home visit
            self._home.set_recent(self._last_task_title, self._recent_tasks)
        else:
            ws_app = self._registry.get(app_id)
            name = ws_app.name if ws_app else app_id
            icon = ws_app.icon if ws_app else "📁"
            desc = ws_app.description if ws_app else ""
            self._active_label.setText(f"{icon}  {name}")
            self._context_label.setText(desc)
            self._home_btn.show()
            self.statusBar().showMessage(
                f"{name} — Preview changes before executing.  "
                "Rollback is always available."
            )

    def _on_nav_clicked(self, app_id: str) -> None:
        self._activate_app(app_id)

    def _on_task_selected(self, task_id: str, task_title: str) -> None:
        """Handle task card click — map task to ResourceHub."""
        self._last_task_title = task_title
        self._recent_tasks.append((task_id, task_title))
        if len(self._recent_tasks) > 5:
            self._recent_tasks = self._recent_tasks[-5:]

        self._activate_app("resourcehub")
        self._context_label.setText(f"Task: {task_title}")
        self.statusBar().showMessage(
            f"{task_title} — Select a folder, then preview and confirm "
            "before executing.  Rollback is always available."
        )

        # Persist immediately so state survives unexpected exit
        self._settings.set_workspace_last_task(task_title)
        titles = [t for _, t in self._recent_tasks]
        self._settings.set_workspace_recent_tasks(titles)

    # ------------------------------------------------------------------
    # Session persistence (M13.4)
    # ------------------------------------------------------------------

    def _restore_session(self) -> str | None:
        """Restore workspace session from QSettings on startup.

        Returns the last active app_id (or None) so the caller can restore
        navigation state.
        """
        last_app = self._settings.get_workspace_last_app()

        task_title = self._settings.get_workspace_last_task()
        if task_title:
            self._last_task_title = task_title

        saved = self._settings.get_workspace_recent_tasks()
        for title in saved:
            self._recent_tasks.append(("recent", title))
        if len(self._recent_tasks) > 5:
            self._recent_tasks = self._recent_tasks[-5:]

        return last_app

    def _save_session(self) -> None:
        """Persist current workspace session to QSettings."""
        if self._active_app_id and self._active_app_id != "home":
            self._settings.set_workspace_last_app(self._active_app_id)
        if self._last_task_title:
            self._settings.set_workspace_last_task(self._last_task_title)
        titles = [t for _, t in self._recent_tasks]
        if titles:
            self._settings.set_workspace_recent_tasks(titles)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._save_session()
        super().closeEvent(event)

