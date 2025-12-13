from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QGridLayout,
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon

import sys
import os
import qdarkstyle
import pathlib

from .connectionPanel import ConnectionPanel
from .pathBar import PathBar

class MasterWindow(QMainWindow):
    
    def __init__(self):
        
        super().__init__()

        # Set window title
        self.setWindowTitle("Master Window")
        p = pathlib.Path(__file__)
        sepa = os.sep
        self.icon = str(p.parent) + sepa + 'icons' + sepa

        self.settings = QSettings(str(p.parent / "interface.ini"), QSettings.Format.IniFormat)

        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setGeometry(100, 30, 1000, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # path
        saved_path = self.settings.value("pathSavingEntry", defaultValue="", type=str)
        self.path_bar = PathBar(saved_path)

        path_container = QHBoxLayout()
        path_container.addStretch()             # add space
        path_container.addWidget(self.path_bar)
        path_container.addStretch()

        main_layout.addLayout(path_container)

        # 2 x 2 grid
        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

        # Top-left label
        laser_label = QLabel("laser")
        laser_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Top-right layout for diags panel
        diags_widget = QWidget()
        diags_layout = QVBoxLayout()
        diags_widget.setLayout(diags_layout)

        diags_label = QLabel("diags")
        diags_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        diags_layout.addWidget(diags_label)

        diagsConnectionPanel = ConnectionPanel()
        diags_layout.addWidget(diagsConnectionPanel)

        # Bottom-left label
        motors_widget = QWidget()
        motors_layout = QVBoxLayout()
        motors_widget.setLayout(motors_layout)

        motors_label = QLabel("motors")
        motors_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        motors_layout.addWidget(motors_label)

        motorsConnectionPanel = ConnectionPanel()
        motors_layout.addWidget(motorsConnectionPanel)

        # Bottom-right label
        bo_label = QLabel("BO")
        bo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to the grid layout
        grid_layout.addWidget(laser_label, 0, 0)
        grid_layout.addWidget(diags_widget, 0, 1)
        grid_layout.addWidget(motors_widget, 1, 0)
        grid_layout.addWidget(bo_label, 1, 1)

        # Set column and row stretch
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        self.actions()

    def actions(self):
        # update the 'interface.ini' file
        self.path_bar.save_entry.textChanged.connect(
            lambda text: self.settings.setValue("pathSavingEntry", text)
        )

    @property
    def path_to_save(self):
        return self.path_bar.path_to_save

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec())