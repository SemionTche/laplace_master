# client/masterClient.py
import zmq
import threading
import time

from PyQt6.QtCore import pyqtSignal

# project
from server_lhc.protocol import (
    CMD_INFO, CMD_PING, CMD_GET,
    make_ping, make_info_request, make_get_request
)

class MasterClient:
    '''
    Class made in order to contact a server.
    '''
    # server_contacted = pyqtSignal(str)  # emits server address when a message is sent

    def __init__(self, address: str, timeout_ms: int = 2000):
        self.address = address
        self.context = zmq.Context.instance()
        self.connected = True
        try:
            self.socket = self.context.socket(zmq.REQ)
            self.socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
            self.socket.setsockopt(zmq.SNDTIMEO, timeout_ms)
            self.socket.connect(address)
        
        except zmq.ZMQError as e:
            raise ValueError(f"Invalid server address: {address}") from e

        self.last_contact_time = 0.0
        self.enabled = True

    def set_connected(self, enabled: bool):
        if self.connected == enabled:
            return  # no change
        self.connected = enabled

        if enabled:
            # recreate the socket if it was disconnected
            try:
                self.socket.close(linger=0)
            except Exception:
                pass

            self.socket = self.context.socket(zmq.REQ)
            self.socket.setsockopt(zmq.RCVTIMEO, 2000)
            self.socket.setsockopt(zmq.SNDTIMEO, 2000)
            self.socket.connect(self.address)
        else:
            # optionally close socket when disabling
            try:
                self.socket.close(linger=0)
            except Exception:
                pass

    def send_message(self, message: dict) -> str | None:
        if not self.connected:
            return None
        try:
            self.socket.send_json(message)
            reply = self.socket.recv_json()
            self.last_contact_time = time.time()
            
            # emit signal through client manager (optional, see note below)
            # self.client_manager.server_contacted.emit(self.address)

            return reply
        except (zmq.error.Again, zmq.ZMQError):
            try:
                self.socket.close(linger=0) # On timeout or invalid socket, just return None
            except Exception:
                pass
            return None

    def ping(self) -> bool:
        if not self.connected:
            return False
        reply = self.send_message(make_ping("Master", "unknown"))
        return reply.get("payload").get("PING") == "PONG"

    def info(self):
        if not self.connected:
            return False
        reply = self.send_message(make_info_request("Master", "unknown"))
        return reply.get("payload")

    def get(self):
        if not self.connected:
            return None
        return self.send_message(
            make_get_request("Master", "unknown")
        )


    # def making_ping(self):
    #     message = {
    #         "from": "Master",
    #         "to": "unknown",
    #         "cmd": "PING",
    #         "payload": {"PING": None},
    #         "version": "1.0",
    #         "error_msg": None,
    #         "msg": "Alive?"
    #     }
    #     return message

    # def making_info(self):
    #     message = {
    #         "from": "Master",
    #         "to" : "unknown",
    #         "cmd": "INFO",
    #         "payload": {
    #             "device": None,
    #             "freedom": 0,
    #             "name": None,
    #             "capabilities": None
    #         },
    #         "version": "1.0",
    #         "msg": "Informations required.",
    #         "error_msg": None
    #     }
    #     return message

    # def making_get(self):
    #     message = {
    #         "from": "Master",
    #         "to": "unknown",
    #         "cmd": "GET",
    #         "payload": {
    #             "data": None
    #         },
    #         "version": "1.0",
    #         "msg": "Get values.",
    #         "error_msg": None
    #     }
    #     return message
    
    def close(self):
        self.socket.close(linger=0)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            try:
                self.socket.close(linger=0)
            except Exception:
                pass
        else:
            # recreate the socket when enabling
            self._reset_socket()

    def _reset_socket(self):
        try:
            self.socket.close(linger=0)
        except Exception:
            pass

        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, 2000)
        self.socket.setsockopt(zmq.SNDTIMEO, 2000)
        self.socket.connect(self.address)