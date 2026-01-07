# libraries
import zmq
import time

# project
from server_lhc.protocol import (
    make_ping, make_info_request, 
    make_get_request, make_save_request
)


class MasterClient:
    '''
    Master client class made in order to contact a server.
    '''
    # server_contacted = pyqtSignal(str)  # emits server address when a message is sent

    def __init__(self, address: str, timeout_ms: int = 2000):
        '''
            Args:
                address: (str)
                    the server address.

                timeout_ms: (int)

        '''
        self.address = address
        self.context = zmq.Context.instance()  # create zmq context
        self.connected = True                  # flag indicating if the client is running
        
        try:
            self.socket = self.context.socket(zmq.REQ)        # create the socket
            self.socket.setsockopt(zmq.RCVTIMEO, timeout_ms)  # set the timeout
            self.socket.setsockopt(zmq.SNDTIMEO, timeout_ms)
            self.socket.connect(address)                      # connect to the address
        
        except zmq.ZMQError as e:
            raise ValueError(f"Invalid server address: {address}") from e

        self.last_contact_time = 0.0
        self.enabled = True
        self.server_name = None
        self.server_decive = None


    def set_connected(self, enabled: bool) -> None:
        if self.connected == enabled:
            return  # no change
        self.connected = enabled

        if enabled:  # recreate the socket if it was disconnected
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

        reply = self.send_message(make_ping("Master", self.server_name))

        if not self._is_valid_reply(reply):
            return False

        return reply.get("payload", {}).get("PING") == "PONG"


    def info(self):
        if not self.connected:
            return None

        reply = self.send_message(make_info_request("Master", self.server_name))

        if not self._is_valid_reply(reply):
            return None

        payload = reply.get("payload", {})
        self.server_name = payload.get("name")
        self.server_decive = payload.get("device")

        return payload


    def get(self):
        if not self.connected:
            return None

        reply = self.send_message(
            make_get_request("Master", self.server_name)
        )

        if not self._is_valid_reply(reply):
            return None

        return reply

    
    def save(self, new_path: str):
        if not self.connected:
            return None

        reply = self.send_message(
            make_save_request("Master", self.server_name, path=new_path)
        )

        if not self._is_valid_reply(reply):
            return None

        return reply

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
    
    def _is_valid_reply(self, reply: dict | None) -> bool:
        if reply is None:
            return False
        if reply.get("error_msg") is not None:
            return False
        return True