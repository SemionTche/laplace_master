from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QIcon

import pathlib
import os

class ServerItemWidget(QWidget):
    
    def __init__(self, 
                 address: str,
                 name: str = "Default"):
        
        super().__init__()
        
        p = pathlib.Path(__file__)
        sepa = os.sep
        self.icon = str(p.parent) + sepa + 'icons' + sepa

        self.connected_icon = QIcon(self.icon + 'connected.png')
        self.disconnected_icon = QIcon(self.icon + 'disconnected.png')

        self.address = address
        self.name = name
        self.connected = True

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)
        self.setLayout(layout)

        # Checkbox (always present, space reserved)
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(20)
        self.checkbox.setEnabled(False)
        layout.addWidget(self.checkbox)

        # State icon
        self.state_icon = QLabel()
        self.state_icon.setFixedWidth(20)
        self.state_icon.setPixmap(self.connected_icon.pixmap(16, 16))
        layout.addWidget(self.state_icon)

        # Address
        self.address_label = QLabel(address)
        layout.addWidget(self.address_label, stretch=2)

        # Name
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label, stretch=1)

        # Last check
        self.last_check_label = QLabel(self._current_time())
        self.last_check_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.last_check_label, stretch=1)

    def _current_time(self) -> str:
        return QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

    def enable_selection(self, enabled: bool):
        self.checkbox.setEnabled(enabled)
        if not enabled:
            self.checkbox.setChecked(False)

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()

    def toggle_connection_state(self):
        self.connected = not self.connected
        icon = self.connected_icon if self.connected else self.disconnected_icon
        self.state_icon.setPixmap(icon.pixmap(16, 16))
        self.update_last_check()

    def update_last_check(self):
        self.last_check_label.setText(self._current_time())
