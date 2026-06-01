# libraries
from laplace_log import log
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, 
    QLabel, QLineEdit, 
    QPushButton
)
from PyQt6.QtCore import pyqtSignal

# project
from utils.config_helper import get_config


class ServerBar(QWidget):
    '''
    Class made to define a QWidget used to group every elements of the server bar.
    The Entry indicates the Ip address of the new server that should be connected.
    '''
    server_added = pyqtSignal(str) # signal for masterWindow

    def __init__(self):
        '''
        Initialization of the class 'ServerBar'.
        It is made to indicate a server address and to transmit
        it to the masterWindow though an emited signal.
        '''
        super().__init__() # heritage of QWidget

        layout = QHBoxLayout()
        self.setLayout(layout)

        # items
        label = QLabel("Add server:")
        self.server_entry = QLineEdit()
        self.server_entry.setPlaceholderText("Server address")

        self.button_auto = QPushButton("Auto")

        # placement
        layout.addWidget(label)
        layout.addWidget(self.server_entry)
        layout.addWidget(self.button_auto)

        # action
        self.server_entry.returnPressed.connect(
            lambda: self._emit_new_server(self.server_entry.text())
        )
        self.button_auto.pressed.connect(self._init_server_auto)


    def _emit_new_server(self, text: str) -> None:
        '''
        Function made to emit a signal when a server address is added.
        Will be catched in 'MasterWindow' to probe the server address
        in 'ClientManager'
        '''
        text = text.strip() # get the address
        
        if text:
            self.server_added.emit(text)    # emit it
            self.server_entry.clear()       # clear the Entry


    def _init_server_auto(self) -> None:
        '''
        Function made to launch the servers automaticaly.
        '''
        log.debug("Auto server init clicked.")
        config = get_config()               # get the config file
        config.beginGroup("init_server")    # look at the group 'init_server'
            
        devices = config.allKeys()          # get all devices in the group
        log.info(f"Probing devices '{devices}' from the config.ini file.")

        for device in devices:
            address = config.value(
                device,
                type=str
            )
            self._emit_new_server(address)
        
        config.endGroup()