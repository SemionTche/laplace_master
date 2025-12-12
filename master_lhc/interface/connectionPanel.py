from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

import os
import pathlib

class ConnectionPanel(QWidget):
    def __init__(self):
        super().__init__()
        p = pathlib.Path(__file__)
        sepa = os.sep
        self.icon = str(p.parent) + sepa+'icons' + sepa

        self.connected_icon = QIcon(self.icon+'connected.png')
        self.disconnected_icon = QIcon(self.icon+'disconnected.png')

        # Internal list
        self.server_list_data = []

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Entry
        self.server_entry = QLineEdit()
        self.server_entry.setPlaceholderText("Add address")
        layout.addWidget(self.server_entry)

        # List
        self.server_list_widget = QListWidget()
        layout.addWidget(self.server_list_widget)

        # Button
        self.disconnect_button = QPushButton("Connect / Disconnect")
        self.disconnect_button.clicked.connect(self.on_disconnect)
        layout.addWidget(self.disconnect_button)

        # Connections
        self.server_entry.returnPressed.connect(self.add_server)

    def add_server(self):
        address = self.server_entry.text()
        if address:
            self.server_list_data.append(address)
            item = QListWidgetItem(self.connected_icon, address)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.server_list_widget.addItem(item)
            self.server_entry.clear()

    def on_disconnect(self):
        for index in range(self.server_list_widget.count()):
            item = self.server_list_widget.item(index)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)

        parent_layout = self.disconnect_button.parentWidget().layout()
        parent_layout.removeWidget(self.disconnect_button)
        self.disconnect_button.deleteLater()

        self.cancel_button = QPushButton("Cancel")
        self.confirm_button = QPushButton("Confirm")
        self.cancel_button.clicked.connect(self.cancel_selection)
        self.confirm_button.clicked.connect(self.confirm_selection)

        parent_layout.addWidget(self.cancel_button)
        parent_layout.addWidget(self.confirm_button)

    def cancel_selection(self):
        for index in range(self.server_list_widget.count()):
            item = self.server_list_widget.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)

        self.restore_disconnect_button()

    def confirm_selection(self):
        for index in range(self.server_list_widget.count()):
            item = self.server_list_widget.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                if item.icon().cacheKey() == self.connected_icon.cacheKey():
                    item.setIcon(self.disconnected_icon)
                else:
                    item.setIcon(self.connected_icon)
                item.setCheckState(Qt.CheckState.Unchecked)

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
