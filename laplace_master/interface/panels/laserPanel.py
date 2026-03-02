# libraries
from laplace_log import log
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, 
    QListWidgetItem, QPushButton, QGroupBox, 
    QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal


class LaserPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.set_up()
        log.info("Laser panel loaded.")
        

    def set_up(self) -> None:
        
        # Main layout
        outer_layout = QVBoxLayout(self)
        
        # Group box
        self.group_box = QGroupBox("Laser system")
        outer_layout.addWidget(self.group_box)

        # inside the group box
        self.main_layout = QVBoxLayout(self.group_box)

        self.shot_number_box = QGroupBox("Shot number:")
        self.main_layout.addWidget(self.shot_number_box)

        self.laser = QGroupBox("Laser:")
        self.main_layout.addWidget(self.laser)