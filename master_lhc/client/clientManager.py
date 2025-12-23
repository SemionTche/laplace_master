import json
from PyQt6.QtCore import QObject, pyqtSignal
from client.masterClient import MasterClient


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
    server_data_received = pyqtSignal(str, dict)  # address, raw data

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
            return ServerInfo(address=address, alive=False, name=None, device=None, freedom=0)

        # Only request name/device if alive
        info = client.info()
        name = info.get("name")
        device = info.get("device")
        freedom = info.get("freedom")
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
            
            if not client.connected:
                continue

            alive = client.ping()
            self.server_pinged.emit(address, alive)

            if not alive:
                continue
            
            self.server_contacted.emit(address)
            data = client.get()
            if data is not None:
                print(f"[GET] {address}: {data}")
                data = data.get("payload").get("data")
                print(f"type = {type(data)}")
                print(f"data = {data}")
                self.server_data_received.emit(address, data)


    def close_all(self):
        for client in self.clients.values():
            client.close()
        self.clients.clear()
    
    def set_server_enabled(self, address: str, enabled: bool):
        print(f"[ClientManager] set_server_enabled({address}, {enabled})")
        client = self.clients.get(address)
        if client:
            client.set_connected(enabled)
    
    def set_optimization_motor_control(self, enabled: bool):
        pass