import zmq
import threading


def connection(address: str):
    print("hello world")


class MasterClient(threading.Thread):

    def __init__(self):
        self.stateOn = True
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)