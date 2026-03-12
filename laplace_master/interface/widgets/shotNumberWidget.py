# libraries
import pathlib

from laplace_log import log
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, 
    QLabel, QCheckBox
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal
from PyQt6.QtGui import QIcon

# project
from .serverItemWidget import ServerItemWidget

class ShotNumberWidget(ServerItemWidget):

    def __init__(self, address: str, name: str, value: int):
        super().__init__(
            address=address, 
            name=name,
            is_value=True
        )