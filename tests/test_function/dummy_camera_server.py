import time
import threading
import zmq
import torch
import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, 
    QVBoxLayout, QLineEdit
)

from laplace_server.server_lhc import ServerLHC
from laplace_server.protocol import DEVICE_CAMERA, make_get_request
from target_function import target_function


CAMERA_ADDRESS = "tcp://*:5556"
MOTOR_ADDRESS = "tcp://147.250.140.65:5555"
SHOT_SUB_ADDRESS = "tcp://147.250.140.65:6009"


class DummyCamera(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dummy Camera")
        self.resize(300, 120)

        self.last_shot = -1
        self.last_result = ""

        self.setup_ui()
        self.setup_zmq()
        self.setup_lhc()

        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    # ---------------- UI ----------------
    def setup_ui(self):
        self.setWindowTitle("Dummy Camera")
        self.resize(360, 220)

        # ---------------- Addresses ----------------
        self.sub_address = QLineEdit(SHOT_SUB_ADDRESS)
        self.sub_address.setReadOnly(True)

        self.motor_address = QLineEdit(MOTOR_ADDRESS)
        self.motor_address.setReadOnly(True)

        self.lhc_address = QLineEdit(CAMERA_ADDRESS)
        self.lhc_address.setReadOnly(True)

        # ---------------- Live values ----------------
        self.shot_label = QLabel("Shot: -")
        self.motor_label = QLabel("Motor: -")
        self.value_label = QLabel("Values: -")
        self.time_label = QLabel("Time: -")

        # ---------------- Style (simple debug look) ----------------
        for w in [self.sub_address, self.motor_address, self.lhc_address]:
            w.setStyleSheet("""
                QLineEdit {
                    background-color: #2b2b2b;
                    color: #00cc66;
                    font-family: monospace;
                    padding: 3px;
                }
            """)

        self.setStyleSheet("""
            QLabel {
                font-size: 13px;
            }
        """)

        # ---------------- Layout ----------------
        layout = QVBoxLayout()

        layout.addWidget(QLabel("SHOT SUB"))
        layout.addWidget(self.sub_address)

        layout.addWidget(QLabel("MOTOR"))
        layout.addWidget(self.motor_address)

        layout.addWidget(QLabel("LHC SERVER"))
        layout.addWidget(self.lhc_address)

        layout.addSpacing(10)

        layout.addWidget(self.shot_label)
        layout.addWidget(self.motor_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.time_label)

        self.setLayout(layout)

    def update_ui(self, shot, motor, timestamp):
        self.shot_label.setText(f"Shot: {shot}")
        self.motor_label.setText(f"Motor: {motor}")
        self.time_label.setText(f"Time: {timestamp}")

    # ---------------- ZMQ ----------------
    def setup_zmq(self):
        self.ctx = zmq.Context()

        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect(SHOT_SUB_ADDRESS)
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "SHOOT")

    # ---------------- LHC ----------------
    def setup_lhc(self):
        self.server = ServerLHC(
            address=CAMERA_ADDRESS,
            freedom=0,
            device=DEVICE_CAMERA,
            data={},
            name="dummy_camera",
            empty_data_after_get=True,
        )
        self.server.start()

    # ---------------- Motor ----------------
    def get_motor(self):
        sock = self.ctx.socket(zmq.REQ)
        sock.connect(MOTOR_ADDRESS)

        sock.send_json(make_get_request("camera", "dummy_motor"))
        reply = sock.recv_json()

        sock.close()

        return reply["payload"]["data"]["positions"]

    # ---------------- Measure ----------------
    def measure(self, shot):
        x1, x2 = self.get_motor()

        x1 = torch.tensor(x1)
        x2 = torch.tensor(x2)

        r = target_function(x1, x2)

        self.value_label.setText(f"Value: {r[:, 0].tolist()} charge | {r[:, 1].tolist()} energy")

        return {
            "shot_number": shot,
            "motor": [x1.item(), x2.item()],
            "charge": r[:, 0].tolist(),
            "energy": r[:, 1].tolist(),
            "time": time.strftime("%H:%M:%S"),
        }

    # ---------------- Loop ----------------
    def loop(self):
        print("Camera listening...")

        while self.running:
            try:
                topic = self.sub.recv_string()
                event = self.sub.recv_json()

                shot = event["number"]

                data = self.measure(shot)
                self.server.set_data(data)

                self.update_ui(
                    shot,
                    data["motor"],
                    data["time"]
                )

                self.last_shot = shot

                print("Camera triggered:", shot)

            except Exception as e:
                if self.running:
                    print("camera error:", e)


    def closeEvent(self, event):
        self.running = False
        time.sleep(0.1)
        self.server.stop()
        self.sub.close()
        self.ctx.term()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    cam = DummyCamera()
    cam.show()
    sys.exit(app.exec())