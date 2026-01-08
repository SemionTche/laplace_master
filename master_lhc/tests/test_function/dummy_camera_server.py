import time
import zmq
import torch

from server_lhc.serverLHC import ServerLHC
from server_lhc.protocol import (
    DEVICE_CAMERA,
    make_get_request
)

from target_function import target_function

CAMERA_ADDRESS = "tcp://*:5556"
MOTOR_ADDRESS  = "tcp://147.250.140.65:5555"


class DummyCamera:
    def __init__(self, motor_address):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.REQ)
        self.socket.connect(motor_address)

    def read_motor_position(self):
        self.socket.send_json(
            make_get_request(sender="camera", target="dummy_motor")
        )
        reply = self.socket.recv_json()
        return reply["payload"]["data"]["positions"]

    def measure(self):
        x1, x2 = self.read_motor_position()
        x1 = torch.tensor(x1)
        x2 = torch.tensor(x2)

        y = target_function(x1, x2)
        return y.squeeze(0).tolist()


if __name__ == "__main__":

    camera = DummyCamera(MOTOR_ADDRESS)

    server = ServerLHC(
        address=CAMERA_ADDRESS,
        freedom=2,
        device=DEVICE_CAMERA,
        data={"value": [0.0, 0.0]},
        name="dummy_camera"
    )

    def on_get():
        value = camera.measure()
        print(f"[Camera] Measured {value}")
        server.set_data({"value": value})

    server.set_on_get(on_get)

    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
