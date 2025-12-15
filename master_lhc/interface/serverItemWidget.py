from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal
from PyQt6.QtGui import QIcon

import pathlib
import os

class ServerItemWidget(QWidget):
    '''
    Class made to define the line content in 'ConnectionPanel'.
    Display the element related to the server as a 'QWidget'.
    
    A flag 'self.connected' indicates if the communication should
    be made with the server.
    '''
    connection_changed = pyqtSignal(str, bool)  # address, connected
    def __init__(self, 
                 address: str,
                 name: str = "Unkown"):
        '''
        Initialization of the 'ServerItemWidget' class.
        This class is made to build a widget displaying
        relevant informations about a server.

            Args:
                address: (str)
                    The Ip address of the server.
                
                name: (str)
                    The name of the server.
        '''
        
        super().__init__() # heritage from QWidget
        
        p = pathlib.Path(__file__)                          # get the path of the file
        sepa = os.sep                                       # define the separator no matter of the os
        self.icon = str(p.parent) + sepa + 'icons' + sepa   # path to the icon folder

        # build the check and uncheck icons
        self.connected_icon = QIcon(self.icon + 'connected.png')
        self.disconnected_icon = QIcon(self.icon + 'disconnected.png')

        self.address = address
        self.name = name
        self.connected = True # flag that defines if the server should be 'connected' (to send messages)

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2) # aspect of the line
        layout.setSpacing(8)
        self.setLayout(layout)

        # checkBox (that change the flag 'self.connected')
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(20)
        self.checkbox.setEnabled(False)
        layout.addWidget(self.checkbox)

        # state icon
        self.state_icon = QLabel() # creat a blanck label
        self.state_icon.setFixedWidth(20)
        self.state_icon.setPixmap(self.connected_icon.pixmap(16, 16)) # add an image
        layout.addWidget(self.state_icon)

        # address
        self.address_label = QLabel(address)
        layout.addWidget(self.address_label, stretch=2)

        # name
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label, stretch=1)

        # last check
        self.last_check_label = QLabel(self._current_time())
        self.last_check_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.last_check_label, stretch=1)


    def _current_time(self) -> str:
        '''
        Return the current time of the master.
        '''
        return QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")


    def enable_selection(self, enabled: bool) -> None:
        '''
        Function made to handle the enabled / disabled feature 
        of the checkBox.
        
            Arg:
                enabled: (bool)
                    indicates if the checkBox should be enabled or disabled.
        '''
        self.checkbox.setEnabled(enabled)
        if not enabled:
            self.checkbox.setChecked(False)


    def is_selected(self) -> bool:
        '''
        Conveniant function to access to the statut 'connected'
        of the server.
        '''
        return self.checkbox.isChecked()


    def toggle_connection_state(self) -> None:
        '''
        Function made to change the flag 'self.connected'.
        '''
        self.connected = not self.connected # change the flag
        # change the icon
        icon = self.connected_icon if self.connected else self.disconnected_icon
        self.state_icon.setPixmap(icon.pixmap(16, 16))
        
        self.update_last_check() # update the last check time

        # Emit the signal
        self.connection_changed.emit(self.address, self.connected)


    def update_last_check(self) -> None:
        '''
        Update the last time at which the server as been checked.
        '''
        self.last_check_label.setText(self._current_time())

    def set_name(self, name: str):
        self.name_label.setText(name)