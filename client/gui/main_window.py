from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt

from enum import Enum
from hashlib import sha256
from base64 import b64decode
import rsa

from gui.shared import header_font, general_font, small_font
from gui.log_widget import LogWidget
from gui.message_dialog import MessageDialog

from api_request import request

class MainWindow(QWidget):
    class Page(Enum):
        Home = 0
        Send = 1
        Verify = 2

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.current_page = MainWindow.Page.Home

        self.caption_label = QLabel("Caption")
        self.caption_label.setFont(header_font)

        self.send_message_btn = QPushButton("Send message")
        self.send_message_btn.setFont(general_font)
        self.send_message_btn.setFixedWidth(175)
        self.send_message_btn.clicked.connect(self.on_send_message_btn_clicked)

        self.verify_message_btn = QPushButton("Verify message")
        self.verify_message_btn.setFont(general_font)
        self.verify_message_btn.setFixedWidth(175)
        self.verify_message_btn.clicked.connect(self.on_verify_message_btn_clicked)

        self.select_task_container =QWidget()

        self.select_task_layout = QVBoxLayout(self.select_task_container)
        self.select_task_layout.addWidget(self.send_message_btn, alignment=Qt.AlignCenter)
        self.select_task_layout.addWidget(self.verify_message_btn, alignment=Qt.AlignCenter)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFont(general_font)
        self.cancel_btn.clicked.connect(self.on_cancel_btn_clicked)

        self.correct_action_btn = QPushButton("Correct action")
        self.correct_action_btn.setFont(general_font)
        self.correct_action_btn.clicked.connect(self.on_correct_action_btn_clicked)

        self.incorrect_action_btn = QPushButton("Incorrect action")
        self.incorrect_action_btn.setFont(general_font)
        self.incorrect_action_btn.clicked.connect(self.on_incorrect_action_btn_clicked)

        self.actions_container = QWidget()

        self.actions_layout = QHBoxLayout(self.actions_container)
        self.actions_layout.addStretch(0)
        self.actions_layout.addWidget(self.cancel_btn, alignment=Qt.AlignCenter)
        self.actions_layout.addWidget(self.correct_action_btn, alignment=Qt.AlignCenter)
        self.actions_layout.addWidget(self.incorrect_action_btn, alignment=Qt.AlignCenter)
        self.actions_layout.addStretch(0)

        self.log_widget = LogWidget()
        self.log_widget.setFont(small_font)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.caption_label, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.select_task_container)
        self.main_layout.addWidget(self.actions_container)
        self.main_layout.addWidget(self.log_widget, 1)
        self.main_layout.addStretch(0)

        self.on_cancel_btn_clicked()

    def on_cancel_btn_clicked(self):
        self.current_page = MainWindow.Page.Home
        self.caption_label.setText("Choose action")

        self.select_task_container.setVisible(True)
        self.log_widget.setVisible(False)
        self.actions_container.setVisible(False)

    def on_send_message_btn_clicked(self):
        self.current_page = MainWindow.Page.Send
        self.caption_label.setText("Send message")

        self.select_task_container.setVisible(False)
        self.log_widget.setVisible(True)
        self.actions_container.setVisible(True)

        self.correct_action_btn.setText("Send correct message")
        self.incorrect_action_btn.setText("Send incorrect message")

    def on_verify_message_btn_clicked(self):
        self.current_page = MainWindow.Page.Verify
        self.caption_label.setText("Verify message")

        self.select_task_container.setVisible(False)
        self.log_widget.setVisible(True)
        self.actions_container.setVisible(True)

        self.correct_action_btn.setText("Request correct message")
        self.incorrect_action_btn.setText("Request incorrect message")

    def on_correct_action_btn_clicked(self):
        if self.current_page == MainWindow.Page.Send:
            self.send_message(True)

        if self.current_page == MainWindow.Page.Verify:
            self.verify_message(True)

    def on_incorrect_action_btn_clicked(self):
        if self.current_page == MainWindow.Page.Send:
            self.send_message(False)

        if self.current_page == MainWindow.Page.Verify:
            self.verify_message(False)

    def send_message(self, correct):
        self.log_widget.add_info("Start a new task - Send message to verify")

        dialog = MessageDialog(self)
        if not dialog.exec():
            self.log_widget.add_error("Task canceled")
            return

        message = dialog.message()
        hash = sha256(message.encode())
        signature = rsa.sign(hash.hexdigest().encode(), request.private_key, "SHA-1")

        self.log_widget.add_info(f"Send message - \"{message}\"")

        if request.verify_message(message if correct else message + "Fake data", signature):
            self.log_widget.add_success("Correct")
        else:
            self.log_widget.add_error("Incorrect")

    def verify_message(self, correct):
        self.log_widget.add_info("Start a new task - Verify message from server")

        json_public_key = request.get_public_key()
        if json_public_key is None:
            self.log_widget.add_error("Can't retrieve public key")
            return

        json_message = request.get_message(correct)
        if json_message is None:
            self.log_widget.add_error("Can't retrieve message")
            return

        message = json_message["message"]
        self.log_widget.add_info(f"Received message - \"{message}\"")

        hash = sha256(message.encode()).hexdigest().encode()
        signature = b64decode(json_message["signature"])
        server_public_key = rsa.PublicKey(int(json_public_key["n"]), int(json_public_key["e"]))

        try:
            rsa.verify(hash, signature, server_public_key)

        except rsa.VerificationError:
            self.log_widget.add_error("Received an incorrect message")
            return

        self.log_widget.add_success("Received the correct message")