# libraries
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit
)
from PyQt6.QtCore import pyqtSignal

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

        # placement
        layout.addWidget(label)
        layout.addWidget(self.server_entry)

        # action
        self.server_entry.returnPressed.connect(self._emit_new_server)

    def _emit_new_server(self) -> None:
        '''
        Function made to emit a signal when a server address is added.
        Will be catched in 'MasterWindow' to probe the server address
        in 'ClientManager'
        '''
        text = self.server_entry.text().strip() # get the address
        if text:
            self.server_added.emit(text)    # emit it
            self.server_entry.clear()       # clear the Entry
