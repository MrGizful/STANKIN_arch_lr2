from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QLabel, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy

from gui.shared import header_font, general_font

class MessageDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.caption_label = QLabel("Enter message to send")
        self.caption_label.setFont(header_font)

        self.message_box = QTextEdit()
        self.message_box.setFont(general_font)
        self.message_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.ok_btn = QPushButton("Ok")
        self.ok_btn.setFont(general_font)
        self.ok_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFont(general_font)
        self.cancel_btn.clicked.connect(self.reject)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch(0)
        self.btn_layout.addWidget(self.ok_btn)
        self.btn_layout.addWidget(self.cancel_btn)
        self.btn_layout.addStretch(0)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.caption_label, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.message_box)
        self.main_layout.addLayout(self.btn_layout)

    def message(self):
        return self.message_box.toPlainText()