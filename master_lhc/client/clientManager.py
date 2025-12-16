import time
from PyQt6.QtCore import QObject, pyqtSignal
from .masterClient import MasterClient


from dataclasses import dataclass

@dataclass
class ServerInfo:
    address: str
    alive: bool
    name: str | None
    device: str | None
    freedom : int


class ClientManager(QObject):
    
    server_pinged = pyqtSignal(str, bool)  # address, alive
    server_contacted = pyqtSignal(str)     # address
    server_identified = pyqtSignal(str, str)  # address, name

    def __init__(self):
        super().__init__()
        self.clients: dict[str, MasterClient] = {}

    def probe_server(self, address: str) -> ServerInfo | None:
        try:
            client = MasterClient(address)
        except ValueError:
            return None

        self.clients[address] = client

        alive = client.ping()
        if not alive:
            client.close()
            return ServerInfo(address=address, alive=False, name=None, device=None, serverControledLines=0)

        # Only request name/device if alive
        name = client.send_message("__NAME__")
        device = client.send_message("__DEVICE__")
        freedom = client.send_message("__FREEDOM__")
        try:
            freedom = int(freedom)
        except (TypeError, ValueError):
            freedom = 0
        return ServerInfo(address=address, alive=True, name=name, device=device, freedom=freedom)

    def remove_server(self, address: str):
        client = self.clients.pop(address, None)
        if client:
            client.close()

    def ping_all(self):
        for address, client in self.clients.items():
            alive = client.ping()
            self.server_pinged.emit(address, alive)

            # if client.connected and alive:
            if alive:
                self.server_contacted.emit(address)


    def close_all(self):
        for client in self.clients.values():
            client.close()
        self.clients.clear()
    
    def set_server_enabled(self, address: str, enabled: bool):
        print(f"[ClientManager] set_server_enabled({address}, {enabled})")
        client = self.clients.get(address)
        if client:
            client.set_connected(enabled)