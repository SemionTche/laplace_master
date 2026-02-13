# libraries
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QGridLayout,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QIcon

import pathlib
import qdarkstyle

from laplace_server.protocol import (
    CMD_INFO, CMD_PING, CMD_GET, CMD_SAVE, CMD_STOP,
    DEVICE_MOTOR, DEVICE_CAMERA, DEVICE_GAS, DEVICE_OPT
)

# project
from interface.connectionPanel import ConnectionPanel
from interface.optimizationPanel import OptimizationPanel
from interface.saveBar import SaveBar
from interface.serverBar import ServerBar
from client.clientManager import ClientManager
from client.brain import Brain

class MasterWindow(QMainWindow):
    '''
    Main class of the 'master_lhc' project.
    Create the main window and connect the interface 
    and the server configurations. 
    '''
    def __init__(self):
        '''
        Initialization of the 'MasterWindow' class.
        '''
        super().__init__() # heritage from QMainWindow

        self.p = pathlib.Path(__file__)  # current path of the file
        
        # load the settings
        self.settings = QSettings(str(self.p.parent.parent / "config.ini"), QSettings.Format.IniFormat)

        self.set_up()  # initialize the widgets and place them in the window

        # Manager handling one client per server
        self.client_manager = ClientManager()
        self.brain = Brain(self.client_manager)
        
        # Ping timer
        self.timer = QTimer()
        ping_time_ms = self.settings.value("server/ping_time_ms", defaultValue=3000, type=int)
        self.timer.start(ping_time_ms)
        
        self.actions()  # signals


    @property
    def saving_path(self) -> str:
        '''
        Property made to have a conveniant access to the saving path.
        '''
        return self.save_bar.saving_path


    def set_up(self) -> None:
        '''
        Function made to initialize the widgets and to place them in the 'MasterWindow'.
        '''
        # Set window title, geometry and style
        self.setWindowTitle("Master Window")
        self.setGeometry(100, 30, 1000, 700)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        
        # Window icon
        icon_path = self.p.parent / 'icons'    # icon path
        self.setWindowIcon(QIcon(str(icon_path / 'LOA.png')))

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        ### top line (saveBar and serverBar)
        top_container = QHBoxLayout()
        main_layout.addLayout(top_container)

            # pathBar
        saved_path = self.settings.value("interface/path_saving_entry", defaultValue="", type=str)
        self.save_bar = SaveBar(saved_path)

        # top_container.addStretch(3)          # add space
        top_container.addWidget(self.save_bar)
        # top_container.addStretch(2)

            # serverBar
        self.server_bar = ServerBar()
        top_container.addWidget(self.server_bar)
        # top_container.addStretch(3)

        ### 2 x 2 grid
        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

            # Top-left label
        laser_label = QLabel("laser")
        laser_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Top-right layout for diags panel
        self.diagsConnectionPanel = ConnectionPanel("Diagnostics")

            # Bottom-left label
        self.motorsConnectionPanel = ConnectionPanel("Control systems")

            # Bottom-right label
        self.optimizationPanel = OptimizationPanel()

            # Add widgets to the grid layout
        grid_layout.addWidget(laser_label, 0, 0)
        grid_layout.addWidget(self.diagsConnectionPanel, 0, 1)
        grid_layout.addWidget(self.motorsConnectionPanel, 1, 0)
        grid_layout.addWidget(self.optimizationPanel, 1, 1)

            # Set column and row stretch
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)


    def actions(self) -> None:
        '''
        Defines all the signals between the clients and the interface.
        '''
        # update the 'config.ini' file when the 'path saving entry' is modified
        self.save_bar.save_entry.textChanged.connect(
            lambda text: self.settings.setValue("interface/path_saving_entry", text)
        )

        self.save_bar.save_entry.textChanged.connect(
            self.client_manager.save_all
        )

        # when a server address is given, use the route procedure
        self.server_bar.server_added.connect(self.route_server)
        
        self.client_manager.server_contacted.connect(
            self.diagsConnectionPanel.update_server_last_msg
        )
        
        self.client_manager.server_identified.connect(
            self.diagsConnectionPanel.update_server_name
        )
        
        self.timer.timeout.connect(
            self.client_manager.ping_all
        )

        self.diagsConnectionPanel.server_connection_changed.connect(
            lambda addr, state: self.client_manager.set_server_enabled(addr, state)
        )
        self.motorsConnectionPanel.server_connection_changed.connect(
            lambda addr, state: self.client_manager.set_server_enabled(addr, state)
        )
        self.optimizationPanel.server_connection_changed.connect(
            lambda addr, state: self.client_manager.set_server_enabled(addr, state)
        )

        ### update last msg time every panel
        self.client_manager.server_contacted.connect(
            self.diagsConnectionPanel.update_server_last_msg
        )

        self.client_manager.server_contacted.connect(
            self.motorsConnectionPanel.update_server_last_msg
        )

        self.client_manager.server_contacted.connect(
            self.optimizationPanel.update_server_last_msg
        )

        ### update server state in every panel
        self.client_manager.server_pinged.connect(
            self.diagsConnectionPanel.on_server_alive_changed
        )

        self.client_manager.server_pinged.connect(
            self.motorsConnectionPanel.on_server_alive_changed
        )

        self.client_manager.server_pinged.connect(
            self.optimizationPanel.on_server_alive_changed
        )

        ### 
        self.client_manager.server_data_received.connect(
            self.motorsConnectionPanel.update_server_data
        )

        # self.optimizationPanel.motor_control_changed.connect(
        #     self.client_manager.set_optimization_motor_control
        # )

        self.optimizationPanel.motor_control_changed.connect(
            self.brain.set_motor_control
        )

        self.optimizationPanel.next_queue_clicked.connect(
            self.brain._next
        )

        # self.client_manager.server_data_received.connect(
        #     self.client_manager.handle_opt_data
        # )

        self.client_manager.server_data_received.connect(
            self.brain.on_opt_data
        )

        self.client_manager.server_data_received.connect(
            self.brain.on_measurement
        )

    def route_server(self, address: str) -> None:
        '''
        Function called when a new server address is provided.
        Probe the server and use the informations gather to create 
        the elements in the corresponding 'connectionPanel'.

            Errors: message boxes are shown when the address is
            not conform to the ZMQ standards and when the client
            did get not answer.

            Arg:
                address: (str)
                    the address of the server in ZMQ
                    format, using REQ.
        '''
        # probe the server to gather informations
        info = self.client_manager.probe_server(address, self.saving_path)
        
        # if there is no information (an error was raised)
        if info is None:
            # create a message box
            QMessageBox.warning(self, "Invalid address",
            f'The address "{address}" was not found or is invalid.',
            QMessageBox.StandardButton.Ok)
            return                  # get out of the routing session

        # if the client did get not answer
        if not info.alive:
            # create a message box
            QMessageBox.warning(self, "Server unreachable",
            f'The server "{address}" did not respond.',
            QMessageBox.StandardButton.Ok)
            return                 # get out of the routing session

        # if the device is a camera
        if info.device == DEVICE_CAMERA:
            # top right connectionPanel
            self.diagsConnectionPanel.add_server(
                address=info.address,
                name=info.name or "Unknown"
            )
        
        # elif the device is an 'operating systems'
        elif info.device == DEVICE_MOTOR or info.device == DEVICE_GAS:
            # bottom left connectionPanel
            self.motorsConnectionPanel.add_server(
                address=info.address,
                name=info.name or "Unkwon"
            )
            # create a subline per degree of freedom
            if info.freedom:
                self.motorsConnectionPanel.add_server_controls(
                    info.address,
                    info.freedom
                )
        
        elif info.device == DEVICE_OPT:
            self.optimizationPanel.add_server(
                address=info.address,
                name=info.name or "Optimization"
            )


    def closeEvent(self, event) -> None:
        '''
        Function called when the window is closing.
        Close every client of client manager.
        '''
        self.client_manager.close_all()
        event.accept()