from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.workspace_window import WorkspaceWindow


def main() -> None:
    app = QApplication(sys.argv)
    window = WorkspaceWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
