# libraries
import pathlib

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, 
    QLabel, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class ServerControlWidget(QWidget):
    '''
    '''
    def __init__(self, address: str, motor_index: int):
        '''

            Args:
                address: (str)
                    the server address.
                
                motor_index: (int)
                    the corresponding number in the server degree of freedom.
        '''
        
        super().__init__() # heritage from QWidget

        self.address = address
        self.motor_index = motor_index
        self.connected = True  # connection flag

        # icons
        p = pathlib.Path(__file__)               # get the path of the file
        icon_path = p.parent.parent / "icons"    # path to the icon folder
        
        # build the check and uncheck icons
        self.connected_icon = QIcon(str(icon_path / "connected.png"))
        self.disconnected_icon = QIcon(str(icon_path / "disconnected.png"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 2, 4, 2)  # indent
        layout.setSpacing(8)

        self.setMinimumHeight(26)

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

        # unit
        self.unit = QLabel("")
        layout.addWidget(self.unit, stretch=1)


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


    def update_positions(self, position: float, unit: str):
        self.value.setText(f"{float(position):.5f}")
        self.unit.setText(str(unit))