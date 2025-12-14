# client/masterClient.py
import zmq
import threading
import time


class MasterClient:
    def __init__(self, address: str, timeout_ms: int = 2000):
        self.address = address
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.REQ)

        self.socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
        self.socket.setsockopt(zmq.SNDTIMEO, timeout_ms)

        self.socket.connect(address)

        self.last_contact_time = 0.0

    def send_message(self, message: str) -> str | None:
        try:

            self.socket.send_string(message)
            reply = self.socket.recv_string()
            self.last_contact_time = time.time()
            
            return reply
        
        except zmq.error.Again: # timeout
            return None

    def ping(self) -> bool:
        reply = self.send_message("PING")
        return reply == "PONG"

    def close(self):
        self.socket.close(linger=0)
