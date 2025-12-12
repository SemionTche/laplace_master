from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout
from PyQt6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import sys
import os
import qdarkstyle
import pathlib

from connectionPanel import ConnectionPanel

class masterWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Master Window")
        p = pathlib.Path(__file__)
        sepa = os.sep
        self.icon = str(p.parent) + sepa+'icons' + sepa

        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setGeometry(100, 30, 1200, 800)

        # Server list for diags panel
        self.server_list_data = []

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create grid layout to divide window into four areas
        layout = QGridLayout()
        central_widget.setLayout(layout)

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
        layout.addWidget(laser_label, 0, 0)
        layout.addWidget(diags_widget, 0, 1)
        layout.addWidget(motors_widget, 1, 0)
        layout.addWidget(bo_label, 1, 1)

        # Set column and row stretch
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = masterWindow()
    window.show()
    sys.exit(app.exec())