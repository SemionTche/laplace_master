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
    Class defining the sub lines content for the motor control panel.

    This widget represents a degree of freedom of an element of the 
    control system associated with a given server address.

    The flag `self.connected` indicates whether communication with the
    corresponding device server is enabled.
    '''

    def __init__(self, address: str, motor_index: int):
        '''
        Initialization of the 'ServerControlWidget' class.

        This class builds a widget displaying information related to a
        specific motor controlled through a server.

            Args:
                address: (str)
                    The server address associated with this motor.

                motor_index: (int)
                    Index of the motor (degree of freedom) handled
                    by the server.
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


    def enable_selection(self, enabled: bool) -> None:
        '''
        Enable or disable the selection checkbox.

        Arg:
            enabled: (bool)
                Indicates whether the checkbox should be enabled.
        '''
        self.checkbox.setEnabled(enabled)
        if not enabled:
            self.checkbox.setChecked(False)


    def is_selected(self) -> bool:
        '''Return whether the motor is currently selected.'''
        return self.checkbox.isChecked()


    def toggle_connection_state(self) -> None:
        '''
        Toggle the connection flag and update the corresponding icon.

        This method switches the internal communication state and
        visually updates the connection indicator.
        '''
        self.connected = not self.connected

        icon = self.connected_icon if self.connected else self.disconnected_icon
        self.state_icon.setPixmap(icon.pixmap(16, 16))


    def update_positions(self, position: float, unit: str) -> None:
        '''
        Update the displayed motor position and unit.

        Args:
            position: (float)
                Current motor position.

            unit: (str)
                Unit associated with the position.
        '''
        self.value.setText(f"{float(position):.5f}")
        self.unit.setText(str(unit))