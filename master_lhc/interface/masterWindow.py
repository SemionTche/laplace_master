from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QGridLayout,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QIcon

import sys
import os
import qdarkstyle
import pathlib

from .connectionPanel import ConnectionPanel
from .pathBar import PathBar
from .serverBar import ServerBar
from client.clientManager import ClientManager

class MasterWindow(QMainWindow):
    
    def __init__(self):
        
        super().__init__() # heritage from QMainWindow

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

        # top line
        top_container = QHBoxLayout()

        # path
        saved_path = self.settings.value("pathSavingEntry", defaultValue="", type=str)
        self.path_bar = PathBar(saved_path)

        top_container.addStretch()          # add space
        top_container.addWidget(self.path_bar)
        top_container.addStretch()

        # add server
        self.server_bar = ServerBar()
        top_container.addWidget(self.server_bar)
        top_container.addStretch()

        main_layout.addLayout(top_container)

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

        self.diagsConnectionPanel = ConnectionPanel()
        diags_layout.addWidget(self.diagsConnectionPanel)

        # Bottom-left label
        motors_widget = QWidget()
        motors_layout = QVBoxLayout()
        motors_widget.setLayout(motors_layout)

        motors_label = QLabel("motors")
        motors_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        motors_layout.addWidget(motors_label)

        self.motorsConnectionPanel = ConnectionPanel()
        motors_layout.addWidget(self.motorsConnectionPanel)

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

        # client
        self.client_manager = ClientManager()
        self.timer = QTimer()
        self.timer.start(3000)

        self.actions()

    def actions(self):
        # update the 'interface.ini' file
        self.path_bar.save_entry.textChanged.connect(
            lambda text: self.settings.setValue("pathSavingEntry", text)
        )
        self.server_bar.server_added.connect(self.route_server)
        
        self.client_manager.server_contacted.connect(
            self.diagsConnectionPanel.update_last_check
        )
        
        self.client_manager.server_identified.connect(
            self.diagsConnectionPanel.update_server_name
        )
        
        self.timer.timeout.connect(self.client_manager.ping_all)

        self.diagsConnectionPanel.server_connection_changed.connect(
            lambda addr, state: self.client_manager.set_server_enabled(addr, state)
        )
        self.motorsConnectionPanel.server_connection_changed.connect(
            lambda addr, state: self.client_manager.set_server_enabled(addr, state)
        )

        self.client_manager.server_contacted.connect(
            self.diagsConnectionPanel.update_last_check
        )

        self.client_manager.server_contacted.connect(
            self.motorsConnectionPanel.update_last_check
        )

        self.client_manager.server_pinged.connect(
            self.diagsConnectionPanel.on_server_alive_changed
        )
        self.client_manager.server_pinged.connect(
            self.motorsConnectionPanel.on_server_alive_changed
        )

    def route_server(self, address: str):
        info = self.client_manager.probe_server(address)
        
        if info is None:
            QMessageBox.warning(self, "Invalid address",
            f'The address "{address}" was not found or is invalid.',
            QMessageBox.StandardButton.Ok)
            return

        if not info.alive:
            QMessageBox.warning(self, "Server unreachable",
            f'The server "{address}" did not respond.',
            QMessageBox.StandardButton.Ok)
            return

        if info.device == "__CAMERA__":
            self.diagsConnectionPanel.add_server(
                address=info.address,
                name=info.name or "Unknown"
            )
        elif info.device == "__MOTORS__" or info.device == "__GAS__":
            self.motorsConnectionPanel.add_server(
                address=info.address,
                name=info.name or "Unkwon"
            )
            if info.freedom:
                self.motorsConnectionPanel.add_server_controls(
                    info.address,
                    info.freedom
                )

    @property
    def path_to_save(self):
        return self.path_bar.path_to_save

    def closeEvent(self, event):
        self.client_manager.close_all()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec())