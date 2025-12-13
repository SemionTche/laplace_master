from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt

from .serverItemWidget import ServerItemWidget

class ConnectionPanel(QWidget):
    
    def __init__(self):
        
        super().__init__() # heritage from QWidget

        # Internal list of server
        self.server_list_data = []

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # List
        self.server_list_widget = QListWidget()
        layout.addWidget(self.server_list_widget)

        # Button
        self.disconnect_button = QPushButton("Connect / Disconnect")
        self.disconnect_button.clicked.connect(self.on_disconnect)
        layout.addWidget(self.disconnect_button)


    def add_server(self, address=None):

        if not address:
            return

        item = QListWidgetItem(self.server_list_widget)

        widget = ServerItemWidget(address=address, name="Default")

        item.setSizeHint(widget.sizeHint())
        self.server_list_widget.addItem(item)
        self.server_list_widget.setItemWidget(item, widget)


    def on_disconnect(self):
        for i in range(self.server_list_widget.count()):
            widget = self.server_list_widget.itemWidget(
                self.server_list_widget.item(i)
            )
            widget.enable_selection(True)

        self._replace_buttons()



    def cancel_selection(self):
        for i in range(self.server_list_widget.count()):
            widget = self.server_list_widget.itemWidget(
                self.server_list_widget.item(i)
            )
            widget.enable_selection(False)

        self.restore_disconnect_button()



    def confirm_selection(self):
        for i in range(self.server_list_widget.count()):
            widget = self.server_list_widget.itemWidget(
                self.server_list_widget.item(i)
            )
            if widget.is_selected():
                widget.toggle_connection_state()

            widget.enable_selection(False)

        self.restore_disconnect_button()


    def restore_disconnect_button(self):
        parent_layout = self.cancel_button.parentWidget().layout()
        parent_layout.removeWidget(self.cancel_button)
        parent_layout.removeWidget(self.confirm_button)
        self.cancel_button.deleteLater()
        self.confirm_button.deleteLater()

        self.disconnect_button = QPushButton("Connect / Disconnect")
        self.disconnect_button.clicked.connect(self.on_disconnect)
        parent_layout.addWidget(self.disconnect_button)

        for index in range(self.server_list_widget.count()):
            item = self.server_list_widget.item(index)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
    
    def _replace_buttons(self):
        layout = self.disconnect_button.parentWidget().layout()

        layout.removeWidget(self.disconnect_button)
        self.disconnect_button.deleteLater()

        self.cancel_button = QPushButton("Cancel")
        self.confirm_button = QPushButton("Confirm")

        self.cancel_button.clicked.connect(self.cancel_selection)
        self.confirm_button.clicked.connect(self.confirm_selection)

        layout.addWidget(self.cancel_button)
        layout.addWidget(self.confirm_button)

