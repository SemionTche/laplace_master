# libraries
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal

# project
from interface.serverItemWidget import ServerItemWidget
from interface.serverControlWidget import ServerControlWidget

class ConnectionPanel(QWidget):
    '''
    Class made to display a list of server properties.
    Two kinds of line are available: 'ServerItemWidget' and 'ServerControlWidget'.
    The first one is always added for any valid server address.
    The second one is used to control the degree of freedom of the server.
    '''
    # signal to transmit a connection changed from ServerItemWidget
    # to MasterWindow where it will open / close the corresponding client.
    server_connection_changed = pyqtSignal(str, bool)
    
    def __init__(self, title: str = ""):
        '''
        Initialization of the 'ConnectionPanel' class.

            Arg:
                title: (str)
                    the title of the ConnectionPanel
        '''
        
        super().__init__() # heritage from QWidget

        self.title = title  # title of the ConnectionPanel

        # dictionary of the 'ServerItemWidget's stored in the ConnectionPanel 
        self.server_widgets: dict[str, ServerItemWidget] = {}
        
        # dictionary of the 'ServerControlWidget's stored in the ConnectionPanel 
        self.server_control_widgets: dict[str, list[ServerControlWidget]] = {}

        # Internal list of server
        self.server_list_data = []

        ### Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
            
            # title
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

            # list container
        self.server_list_widget = QListWidget()  # QList containing all the widgets displayed (both ServerItemWidget and ServerControlWidget)
        main_layout.addWidget(self.server_list_widget)

            # connect / disconnect button
        self.disconnect_button = QPushButton("Connect / Disconnect")
        self.disconnect_button.clicked.connect(self.on_disconnect)  # use 'on_disconnect" when the button is clicked
        main_layout.addWidget(self.disconnect_button)


    def update_server_name(self, address: str, 
                                 newName: str) -> None:
        '''
        Helper to change the name of the server.
        '''
        widget = self.server_widgets.get(address) # get the widget from the dictionary
        if widget:                                # if there is a widget
            widget.set_name(newName)              # change the name


    def update_server_last_msg(self, address: str):
        '''
        Helper to change the last time a message was received.
        '''
        widget = self.server_widgets.get(address) # get the widget from the dictionary
        if widget:                                # if there is a widget
            widget.update_last_msg()              # change the last time a message was received


    def add_server(self, address: str, 
                            name: str = "Unknown") -> None:
        '''
        Add a server line in the ConnectionPanel.
        Bind the 'connection_changed' signal to the
        function 'on_server_connection_changed'.

            Args:
                address: (str)
                    the server address.
                
                name: (str)
                    the name of the server, default 'Unknown'.
        '''
        # widget is content of the row, item is the layout of the row (size, position, ...)
        item = QListWidgetItem(self.server_list_widget) # create a new list item

        widget = ServerItemWidget(address=address, name=name)                   # initialize the new server line that will be displayed inside the item
        widget.connection_changed.connect(self.on_server_connection_changed)    # bind the signal to emit when the connection changed

        item.setSizeHint(widget.sizeHint())                 # the size of the line
        self.server_list_widget.addItem(item)               # add the new item in the server list
        self.server_list_widget.setItemWidget(item, widget) # assigns the QWidget (widget) that will be rendered inside this row (item)

        self.server_widgets[address] = widget   # add a new address in the dictionary


    def add_server_controls(self, address: str, 
                                  freedom: int) -> None:
        '''
        Add a control line in the ConnectionPanel.

            Args:
                address: (str)
                    the server address.

                freedom: (int)
                    the server degree of freedom.
                    (number of setable elements)
        '''
        self.server_control_widgets[address] = []
        for i in range(freedom):  # for each degree of freedom
            item = QListWidgetItem(self.server_list_widget)
            
            # initialize the new server line that will be displayed inside the item
            widget = ServerControlWidget(address, i + 1)  # number of the element start by 1 rather than 0

            item.setSizeHint(widget.sizeHint())                     # the size of the line
            self.server_list_widget.addItem(item)                   # add the new item in the server list
            self.server_list_widget.setItemWidget(item, widget)     # assigns the QWidget (widget) that will be rendered inside this row (item)
            self.server_control_widgets[address].append(widget)


    def on_disconnect(self) -> None:
        '''
        Function used when the 'Connect / Disconnect' button is pressed. 
        Enable the checkBox of every widget in 'server_list_widget'.
        '''
        for i in range(self.server_list_widget.count()): # for every element in the server list
            # get the current widget
            widget = self.server_list_widget.itemWidget(
                self.server_list_widget.item(i)
            )
            # if it is a compatible widget
            if isinstance(widget, (ServerItemWidget, ServerControlWidget)):
                widget.enable_selection(True)  # enable the checkBox selection

        self._replace_buttons() # create the new button to confirm the selection


    def restore_disconnect_button(self) -> None:
        '''
        Function used to restore the 'Connect / Disconnect' button.
        '''
        parent_layout = self.cancel_button.parentWidget().layout()
        parent_layout.removeWidget(self.cancel_button)                 # remove the buttons
        parent_layout.removeWidget(self.confirm_button)
        self.cancel_button.deleteLater()
        self.confirm_button.deleteLater()

        self.disconnect_button = QPushButton("Connect / Disconnect")   # recreate the button
        self.disconnect_button.clicked.connect(self.on_disconnect)     # bind it
        parent_layout.addWidget(self.disconnect_button)                # add it to the layout

        for index in range(self.server_list_widget.count()):
            item = self.server_list_widget.item(index)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
    

    def _replace_buttons(self) -> None:
        '''
        Function used to replace the 'Connect / Disconnect' button from
        the ConnectionPanel and to replace it with two temporary buttons
        'Confirm' and 'Cancel' that will be destroyed when used.
        '''
        layout = self.disconnect_button.parentWidget().layout()

        layout.removeWidget(self.disconnect_button) # remove the 'Connect / Disconnect' button
        self.disconnect_button.deleteLater()  

        self.cancel_button = QPushButton("Cancel")  # create the new buttons
        self.confirm_button = QPushButton("Confirm")

        self.cancel_button.clicked.connect(self.cancel_selection)  # bind the new buttons
        self.confirm_button.clicked.connect(self.confirm_selection)

        layout.addWidget(self.cancel_button) # add the new buttons
        layout.addWidget(self.confirm_button)


    def cancel_selection(self) -> None:
        '''
        Function made to reset the configuration after using the 'Cancel' button. 
        Disable the checkBox of the widget in the server list and restaure the
        'Connect / Disconnect' button.
        '''
        for i in range(self.server_list_widget.count()): # for every element in the server list
            # get the current widget
            widget = self.server_list_widget.itemWidget(
                self.server_list_widget.item(i)
            )
            # if it is a compatible widget
            if isinstance(widget, (ServerItemWidget, ServerControlWidget)):
                widget.enable_selection(False)  # disable the checkBox selection

        self.restore_disconnect_button()  # restaure the 'Connected / Disconnected' button


    def confirm_selection(self) -> None:
        '''
        Function made to reset the configuration after using the 'Confirm' button. 
        Change the state of the widget selected, disable the checkBox of the widget
        in the server list and restaure the 'Connect / Disconnect' button.
        '''
        for i in range(self.server_list_widget.count()):    # for every element in the server list
            # get the current widget
            widget = self.server_list_widget.itemWidget(
                self.server_list_widget.item(i)
            )
            # if it is a compatible widget
            if isinstance(widget, (ServerItemWidget, ServerControlWidget)):
                if widget.is_selected():
                    widget.toggle_connection_state()  # change the flag and icon of connection state
                widget.enable_selection(False)        # disable the checkBox

        self.restore_disconnect_button() # restaure the 'Connected / Disconnected' button


    def on_server_connection_changed(self, address: str, 
                                         connected: bool) -> None:
        '''
        Function used to transmit a signal from 'ServerItemWidget' 
        to 'MasterWindow' in order to indicate to 'ClientManager'
        which client should be connected / disconnected.

        Change the toggle of the sub 'ServerControlWidget'.
        '''
        print(f"[ConnectionPanel {self.title}] emit {address} {connected}")
        self.server_connection_changed.emit(address, connected)   # emit from ServerItemWidget through MasterWindow to ClientManager

        list_widgets = self.server_control_widgets.get(address)  # get the list of ServerControlWidget associated

        if not list_widgets:  # if there is no sub ServerControlWidget
            return            # get out of the function
        
        for _, widget in enumerate(list_widgets):  # for every sub ServerControlWidget
            widget.toggle_connection_state()       # change the connected flag and icon


    def on_server_alive_changed(self, address: str, alive: bool) -> None:
        '''
        Function used to transmit a message comming from 'ClientManager'
        through 'MasterWindow'. Indicate if a server die (not answering to the ping).
        Change the connection state of the corresponding 'ServerItemWidget'.

            Args:
                address: (str)
                    the server address.
                
                alive: (bool)
                    indicate if the server still answering.
                    (False implies the server is not answering anymore)
        '''
        widget = self.server_widgets.get(address) # get the widget
        if not widget:                            # if there is not server with this address
            return                                # get out of the function

        if not alive and widget.connected:        # if the server stoped to answer and it was consider as connected
            widget.toggle_connection_state()      # change the state of this line
    

    def update_server_data(self, address: str, data: dict):
        '''
        Function made to transmit the data received in ClientManager
        in the corresponding ServerControlWidget to display the current
        position of the operating system.

            Args:
                address: (str)
                    the server address
                
                data: (dict)
                    the dictionary sent by server.
                    Must include a 'positions' key, that return a list 
                    of length equal to the degree of freedom.
        '''
        list_wigets = self.server_control_widgets[address] # get the list freedom of the operating system
        
        if not list_wigets:  # if there is no ServerControlSystem
            return
        
        for i, widget in enumerate(list_wigets):
            if isinstance(widget, ServerControlWidget):
                widget.update_positions(data["positions"][i], data["unit"])
    
        # def update_server_data_from_server_list(self, address: str, data: dict):
        #     '''
        #     hold version.
        #     '''
        #     for i in range(self.server_list_widget.count()):
        #         widget = self.server_list_widget.itemWidget(
        #             self.server_list_widget.item(i)
        #         )
            
        #         if not isinstance(widget, ServerControlWidget):
        #             continue

        #         if widget.address == address:
        #             widget.update_data(data)