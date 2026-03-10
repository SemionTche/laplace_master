# libraries
from laplace_log import log
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, 
    QListWidgetItem, QPushButton, QGroupBox, 
    QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal


# project
from ..widgets import ShotNumberWidget, ServerItemWidget

class LaserPanel(QWidget):

    server_connection_changed = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()

        self.set_up()
        self.server_widgets: dict[str, ServerItemWidget] = {}
        log.info("Laser panel loaded.")
        

    def set_up(self) -> None:
        # Main layout
        outer_layout = QVBoxLayout(self)

        # Group box
        self.group_box = QGroupBox("Laser system")
        outer_layout.addWidget(self.group_box)

        # inside the group box
        self.main_layout = QVBoxLayout(self.group_box)

        # Shot number group box
        self.shot_number_box = QGroupBox("Shot number:")
        self.main_layout.addWidget(self.shot_number_box)
        self.shot_number_layout = QVBoxLayout(self.shot_number_box)

        self.laser = QGroupBox("Laser:")
        self.main_layout.addWidget(self.laser)

        # Connect / Disconnect button
        self.disconnect_button = QPushButton("Connect / Disconnect")
        self.disconnect_button.clicked.connect(self.on_disconnect)
        self.main_layout.addWidget(self.disconnect_button)
        

    def add_shot_number(self, address: str, name: str) -> None:
        widget = ShotNumberWidget(
            name=name,
            address=address,
            value=0
        )
        widget.enable_selection(False)
        widget.connection_changed.connect(self._on_server_connection_changed)

        self.shot_number_layout.addWidget(widget)
        self.server_widgets[address] = widget


    def set_shot_value(self, address: str, data: dict) -> None:
        widget = self.server_widgets.get(address)
        if isinstance(widget, ShotNumberWidget):
            value: int = data.get("shot_number", -1)
            widget.set_value(value)


    def _on_server_connection_changed(self, 
                                      address: str, 
                                      connected: bool) -> None:
        '''
        Emit the signal exactly like ConnectionPanel.
        Enforce single connection and update motor checkbox.
        '''
        log.info(f"[LaserPanel] Server connection status changed | address={address} | connected={connected}")
        self.server_connection_changed.emit(address, connected)
        self._enforce_single_connection()


    def on_disconnect(self) -> None:
        '''
        Enables checkboxes to select server(s) to connect/disconnect.
        '''
        for widget in self.server_widgets.values():
            widget.enable_selection(True)

        # Replace connect button with confirm/cancel
        layout = self.disconnect_button.parentWidget().layout()
        layout.removeWidget(self.disconnect_button)
        self.disconnect_button.deleteLater()

        self.confirm_button = QPushButton("Confirm")
        self.cancel_button = QPushButton("Cancel")
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.cancel_button.clicked.connect(self.cancel_selection)

        layout.addWidget(self.cancel_button)
        layout.addWidget(self.confirm_button)


    def cancel_selection(self) -> None:
        '''
        Cancel selection and restore the connect/disconnect button.
        '''
        for widget in self.server_widgets.values():
            widget.enable_selection(False)
        self._restore_disconnect_button()
    

    def confirm_selection(self) -> None:
        '''
        Confirm selection, toggle connection state, emit signal, and restore button.
        '''
        for widget in self.server_widgets.values():
            if widget.is_selected():
                widget.toggle_connection_state()  # this triggers widget.connection_changed
            widget.enable_selection(False)
        self._enforce_single_connection()
        self._restore_disconnect_button()


    def _restore_disconnect_button(self) -> None:
        layout = self.cancel_button.parentWidget().layout()
        self.cancel_button.deleteLater()
        self.confirm_button.deleteLater()

        self.disconnect_button = QPushButton("Connect / Disconnect")
        self.disconnect_button.clicked.connect(self.on_disconnect)
        layout.addWidget(self.disconnect_button)
    

    def _enforce_single_connection(self) -> None:
        '''
        Disconnect all other servers except the one currently connected.
        '''
        active_server = None
        for addr, widget in self.server_widgets.items():
            if widget.connected:
                if active_server is None:
                    active_server = addr
                else:
                    widget.toggle_connection_state()  # this emits server_connection_changed
    

    def update_server_last_msg(self, address: str) -> None:
        '''
        Helper to change the last time a message was received from a server.
        '''
        widget = self.server_widgets.get(address)
        if widget:
            widget.update_last_msg()
    

    def on_server_alive_changed(self, address: str, alive: bool) -> None:
        '''
        Indicate if a server stops answering.
        '''
        widget = self.server_widgets.get(address)
        if not widget:
            return

        if not alive and widget.connected:
            widget.toggle_connection_state()