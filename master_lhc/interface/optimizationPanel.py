# libraries
from PyQt6.QtWidgets import (
    QWidget, QLabel, QCheckBox, QVBoxLayout
)
from PyQt6.QtCore import pyqtSignal

# project
from interface.serverItemWidget import ServerItemWidget


class OptimizationPanel(QWidget):
    server_connection_changed = pyqtSignal(str, bool)
    motor_control_changed = pyqtSignal(bool)

    def __init__(self, title="Optimization"):
        super().__init__()

        self.server_widget: ServerItemWidget | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(title))

        # placeholder container
        self.server_container = QVBoxLayout()
        layout.addLayout(self.server_container)

        # motor control checkbox
        self.motor_checkbox = QCheckBox("Allow optimization to drive motors")
        self.motor_checkbox.setEnabled(False)
        self.motor_checkbox.toggled.connect(self.motor_control_changed)
        layout.addWidget(self.motor_checkbox)

    def add_server(self, address: str, name: str):
        if self.server_widget is not None:
            return  # only one optimization server allowed

        widget = ServerItemWidget(address=address, name=name)
        widget.connection_changed.connect(self.server_connection_changed)

        self.server_container.addWidget(widget)
        self.server_widget = widget

        self.motor_checkbox.setEnabled(True)