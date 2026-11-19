"""
Sign-in window that pairs the Windows app with a patient account.

Shown on the first launch of SignalSpeak.exe, and whenever the app is
started with --pair (the "Pair with account" shortcut). The patient can
also choose to use SignalSpeak offline, with nothing leaving the computer.

Libraries:
- PySide6 (Qt for Python): https://doc.qt.io/qtforpython-6/
- Requests (through connect.py): https://requests.readthedocs.io

Written with the assistance of Claude Code (Anthropic).
"""

import requests
from PySide6.QtWidgets import (QDialog, QFormLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QVBoxLayout)

from connect import DEFAULT_SERVER, pair


class PairingWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SignalSpeak · Connect to your account")
        self.setMinimumWidth(520)
        self.setStyleSheet("QWidget { font-size: 16px; } QPushButton { padding: 10px 18px; }")

        intro = QLabel(
            "<b>Connect this computer to your patient account</b><br>"
            "This lets your caregiver change your settings and receive your "
            "calls for help. Create the account on the SignalSpeak website first.<br><br>"
            "Your password is used once and is not saved.")
        intro.setWordWrap(True)

        self.server = QLineEdit(DEFAULT_SERVER)
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form = QFormLayout()
        form.addRow("Server address", self.server)
        form.addRow("Patient email", self.email)
        form.addRow("Password", self.password)

        self.message = QLabel()
        self.message.setWordWrap(True)
        self.message.setStyleSheet("color: #b3261e;")

        connect_button = QPushButton("Connect")
        connect_button.setDefault(True)
        connect_button.clicked.connect(self.try_to_pair)
        offline_button = QPushButton("Use offline")
        offline_button.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addWidget(offline_button)
        buttons.addStretch()
        buttons.addWidget(connect_button)

        layout = QVBoxLayout(self)
        layout.addWidget(intro)
        layout.addLayout(form)
        layout.addWidget(self.message)
        layout.addLayout(buttons)

    def try_to_pair(self) -> None:
        self.message.setText("Connecting...")
        self.repaint()
        try:
            account = pair(self.server.text(), self.email.text().strip(),
                           self.password.text())
        except ValueError as error:
            self.message.setText(str(error))
        except requests.RequestException:
            self.message.setText(
                "Could not reach the server. Check the address and that the "
                "SignalSpeak server is running.")
        else:
            self.password.clear()
            self.account = account
            self.accept()


def ask_to_pair() -> bool:
    """Show the window. Returns True if the computer is now paired."""
    return PairingWindow().exec() == QDialog.Accepted
