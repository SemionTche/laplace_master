import time
from PyQt6.QtCore import QObject, pyqtSignal
from .masterClient import MasterClient


class ClientManager(QObject):
    
    server_pinged = pyqtSignal(str, bool)  # address, alive
    server_contacted = pyqtSignal(str)     # address

    def __init__(self):
        super().__init__()
        self.clients: dict[str, MasterClient] = {}

    def add_server(self, address: str):
        if address not in self.clients:
            self.clients[address] = MasterClient(address)

    def remove_server(self, address: str):
        client = self.clients.pop(address, None)
        if client:
            client.close()

    def ping_all(self):
        for address, client in self.clients.items():
            alive = client.ping()
            self.server_pinged.emit(address, alive)


    def close_all(self):
        for client in self.clients.values():
            client.close()
        self.clients.clear()