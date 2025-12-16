from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import pathlib, os

class ServerControlWidget(QWidget):
    def __init__(self, address: str, motor_index: int):
        super().__init__()

        self.address = address
        self.motor_index = motor_index
        self.connected = True  # placeholder flag

        # icons
        p = pathlib.Path(__file__)
        icon_path = p.parent / "icons"
        self.connected_icon = QIcon(str(icon_path / "connected.png"))
        self.disconnected_icon = QIcon(str(icon_path / "disconnected.png"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 2, 4, 2)  # indent
        layout.setSpacing(8)

        # checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(20)
        self.checkbox.setEnabled(False)
        layout.addWidget(self.checkbox)

        # state icon
        self.state_icon = QLabel()
        self.state_icon.setFixedWidth(20)
        self.state_icon.setPixmap(self.connected_icon.pixmap(16, 16))
        layout.addWidget(self.state_icon)

        # label
        self.label = QLabel(f"Motor {motor_index}")
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.label, stretch=1)

        # position
        self.value = QLabel("—")
        layout.addWidget(self.value, stretch=1)

    # --- REQUIRED API ---

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

        # placeholder for later networking
        pass


    def set_position(self, pos: float):
        self.value.setText(f"{pos:.3f}")