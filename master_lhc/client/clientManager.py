#♦ libraries
from PyQt6.QtCore import QObject, pyqtSignal

from dataclasses import dataclass

@dataclass
class ServerInfo:
    '''Class made to define the information received from the server.'''
    address: str
    alive: bool
    name: str | None
    device: str | None
    freedom : int

from server_lhc.protocol import make_set_request, DEVICE_OPT, CMD_OPT

# project
from client.masterClient import MasterClient


class ClientManager(QObject):
    '''
    Class made to organize the clients and send messages to the servers.
    '''
    
    server_pinged = pyqtSignal(str, bool)  # address, alive
    server_contacted = pyqtSignal(str)     # address
    server_identified = pyqtSignal(str, str)  # address, name
    server_data_received = pyqtSignal(str, dict)  # address, raw data

    def __init__(self):
        super().__init__()
        self.clients: dict[str, MasterClient] = {}
        self.server_devices: dict[str, str] = {}

    def probe_server(self, address: str, saving_path: str) -> ServerInfo | None:
        try:
            client = MasterClient(address)
        except ValueError:
            return None

        self.clients[address] = client

        alive = client.ping()
        if not alive:
            client.close()
            return ServerInfo(address=address, alive=False, name=None, device=None, freedom=0)
        
        client.save(saving_path)

        # Only request name/device if alive
        info = client.info()
        if info is not None:
            name = info.get("name")
            device = info.get("device")
            freedom = info.get("freedom")

            self.server_devices[address] = device # store device
            try:
                freedom = int(freedom)
            except (TypeError, ValueError):
                freedom = 0
            return ServerInfo(address=address, alive=True, name=name, device=device, freedom=freedom)
        
        return ServerInfo(address=address, alive=False, name=None, device=None, freedom=0)

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
                self.server_data_received.emit(address, data)

    def save_all(self, new_path: str):
        print(f"the new path is: {new_path}")
        for address, client in self.clients.items():
            if not client.connected:
                continue
            client.save(new_path)

    def close_all(self):
        for client in self.clients.values():
            client.close()
        self.clients.clear()
    
    def set_server_enabled(self, address: str, enabled: bool):
        print(f"[ClientManager] set_server_enabled({address}, {enabled})")
        client = self.clients.get(address)
        if client:
            client.set_connected(enabled)
    
    # def set_optimization_motor_control(self, enabled: bool) -> None:
    #     '''
    #     Enable or disable motor control for optimization.

    #     This function ONLY sets a permission flag.
    #     It does NOT execute optimization commands.
    #     Optimization flow is handled by Brain.
    #     '''
    #     self.is_motor_control = enabled

    
    # def handle_opt_data(self, address: str, data: dict):
    #     print("[OPT] received from", address, data)

    #     if self.server_devices.get(address) != DEVICE_OPT:
    #         return 
    #     if not (data.get("is_init") or data.get("is_opt")):
    #         return

    #     samples = data.get("samples", [])
    #     for sample in samples:
    #         for motor_addr, positions in sample["inputs"].items():
    #             motor_addr = self._normalize_address(motor_addr)
    #             self.optimization_queue.append({
    #                 "motor_address": motor_addr,
    #                 "positions": positions,
    #                 "batch": sample["batch"],
    #                 "candidate": sample["candidate"],
    #             })

    #     self._try_execute_next_optimization_command()


    # def _try_execute_next_optimization_command(self):
    #     if not self.is_motor_control:
    #         return

    #     if not self.optimization_queue:
    #         return

    #     cmd = self.optimization_queue.popleft()

    #     addr = cmd["motor_address"]

    #     client = self.clients.get(addr)
    #     if not client or not client.connected:
    #         print(f"[OPT] Motor {addr} not available")
    #         return

    #     print(f"[OPT] SET {addr} -> {cmd['positions']}")

    #     client.send_message(
    #         make_set_request(
    #             sender="Master",
    #             target=client.server_name,
    #             positions=cmd["positions"]
    #         )
    #     )


    def _normalize_address(self, address: str) -> str:
        if address.startswith("tcp://"):
            return address
        return f"tcp://{address}"
    
    
    def sample_point(self, inputs: dict):
        """
        inputs = { address: position }
        """
        for addr, pos in inputs.items():
            addr = self._normalize_address(addr)
            client = self.clients.get(addr)

            if not client or not client.connected:
                continue

            client.send_message(
                make_set_request(
                    sender="Master",
                    target=client.server_name,
                    positions=pos
                )
            )

    def send_opt(self, address: str, payload: dict):
        """
        Send a SET command to a server (usually DEVICE_OPT).

        Args:
            address: str
                The server address.
            payload: dict
                The payload dictionary to send.
        """
        client = self.clients.get(address)
        if not client or not client.connected:
            print(f"[ClientManager] Cannot send message to {address}: client not connected")
            return

        print(f"[ClientManager] Sending CMD_OPT to {address}: {payload}")

        client.opt_update(data=payload)

        # client.send_message(
        #     make_set_request(sender="Master", target=client.server_name, positions=None, payload=payload)
        # )