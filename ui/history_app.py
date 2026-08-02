from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from engine.operation_logger import OperationLogger
from models.operation_record import OperationRecord

_COLUMNS = ["Time", "Source", "Target", "Result", "Message"]


class HistoryApp(QWidget):
    """History application — read-only view of execution history.

    Lives in the Workspace as a first-class application.
    Reuses the same OperationLogger instance as ResourceHub.
    """

    def __init__(self, logger: OperationLogger,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._logger = logger

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QLabel("Execution History")
        header.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #333;"
        )
        layout.addWidget(header)

        desc = QLabel(
            "Review past file operations.  "
            "Select a row to inspect details."
        )
        desc.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(desc)

        # Table
        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        layout.addWidget(self._table)

        # Actions
        actions = QHBoxLayout()

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self._refresh)
        actions.addWidget(self._refresh_btn)

        actions.addStretch()

        export_btn = QPushButton("Export…")
        export_btn.clicked.connect(self._on_export)
        actions.addWidget(export_btn)

        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self._on_clear)
        actions.addWidget(clear_btn)

        layout.addLayout(actions)

        self._refresh()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _result_label(record: OperationRecord) -> str:
        if not record.success:
            return "Failed"
        if record.message == "已跳过":
            return "Skipped"
        return "Success"

    def _refresh(self) -> None:
        records = self._logger.records()
        self._table.setRowCount(len(records))
        for row, rec in enumerate(records):
            self._table.setItem(row, 0, QTableWidgetItem(
                rec.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            ))
            self._table.setItem(row, 1, QTableWidgetItem(str(rec.source)))
            self._table.setItem(row, 2, QTableWidgetItem(str(rec.target)))
            self._table.setItem(row, 3, QTableWidgetItem(
                self._result_label(rec)))
            self._table.setItem(row, 4, QTableWidgetItem(rec.message))

        count = len(records)
        self._refresh_btn.setText(
            f"Refresh ({count} record{'s' if count != 1 else ''})"
        )

    def _on_clear(self) -> None:
        self._logger.clear()
        self._refresh()

    def _on_export(self) -> None:
        records = self._logger.records()
        if not records:
            QMessageBox.information(self, "Export", "No records to export.")
            return

        path_str, _ = QFileDialog.getSaveFileName(
            self, "Export History", "", "CSV (*.csv);;TXT (*.txt)",
        )
        if not path_str:
            return

        path = Path(path_str)
        try:
            if path.suffix.lower() == ".csv":
                self._export_csv(records, path)
            else:
                self._export_txt(records, path)
        except OSError:
            QMessageBox.warning(
                self, "Export Failed", "Could not write export file.")

    @staticmethod
    def _export_csv(records: list[OperationRecord], path: Path) -> None:
        lines = ["time,source,target,result,message"]
        for rec in records:
            result = HistoryApp._result_label(rec)
            lines.append(
                f"{rec.timestamp.strftime('%Y-%m-%d %H:%M:%S')},"
                f'"{rec.source}","{rec.target}",{result},"{rec.message}"'
            )
        path.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _export_txt(records: list[OperationRecord], path: Path) -> None:
        lines: list[str] = []
        for rec in records:
            result = HistoryApp._result_label(rec)
            lines.append(
                f"[{rec.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"{rec.source} → {rec.target} | {result} | {rec.message}"
            )
        path.write_text("\n".join(lines), encoding="utf-8")
