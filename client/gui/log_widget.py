from PySide6.QtWidgets import QWidget, QTextEdit, QSizePolicy
from PySide6.QtCore import Qt

from datetime import datetime

class LogWidget(QTextEdit):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        self.setReadOnly(True)

    def append(self, message, color):
        current_time = datetime.now().strftime("%H:%M:%S")

        content = f"<span style=\" color:{color};\" >"
        content += f"[{current_time}] : {message}"
        content += "</span>"

        super().append(content)

    def add_info(self, message):
        self.append(message, "#000000")

    def add_error(self, message):
        self.append(message, "#ff0000")

    def add_success(self, message):
        self.append(message, "#156605")