from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import pyqtSignal


class ServerBar(QWidget):

    server_added = pyqtSignal(str)

    def __init__(self):
        
        super().__init__()

        self.setMaximumWidth(1000)

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel("Add server:")
        self.server_entry = QLineEdit()
        self.server_entry.setPlaceholderText("Server address")

        layout.addWidget(label)
        layout.addWidget(self.server_entry)

        self.server_entry.returnPressed.connect(self._emit_server)

    def _emit_server(self):
        text = self.server_entry.text().strip()
        if text:
            self.server_added.emit(text)
            self.server_entry.clear()
