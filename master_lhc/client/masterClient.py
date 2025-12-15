# client/masterClient.py
import zmq
import threading
import time


class MasterClient:
    def __init__(self, address: str, timeout_ms: int = 2000):
        self.address = address
        self.context = zmq.Context.instance()

        try:
            self.socket = self.context.socket(zmq.REQ)
            self.socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
            self.socket.setsockopt(zmq.SNDTIMEO, timeout_ms)
            self.socket.connect(address)
        
        except zmq.ZMQError as e:
            raise ValueError(f"Invalid server address: {address}") from e

        self.last_contact_time = 0.0

    def send_message(self, message: str) -> str | None:
        try:

            self.socket.send_string(message)
            reply = self.socket.recv_string()
            self.last_contact_time = time.time()
            
            return reply
        
        except zmq.error.Again:
            self._reset_socket() # Timeout → socket is now invalid
            return None

    def ping(self) -> bool:
        reply = self.send_message("__PING__")
        return reply == "__PONG__"

    def close(self):
        self.socket.close(linger=0)
    
    def _reset_socket(self):
        try:
            self.socket.close(linger=0)
        except Exception:
            pass

        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, 2000)
        self.socket.setsockopt(zmq.SNDTIMEO, 2000)
        self.socket.connect(self.address)
