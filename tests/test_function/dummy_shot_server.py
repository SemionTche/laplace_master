import sys
import time
import zmq
import socket as sock

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QSpinBox, QVBoxLayout, QHBoxLayout, QLineEdit
)
from PyQt6.QtCore import Qt

from laplace_server.server_lhc import ServerLHC
from laplace_server.protocol import DEVICE_SHOT


PUB_PORT = 6009
LHC_ADDRESS = "tcp://*:7892"


class DummyShot(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dummy Shot Device")
        self.resize(360, 140)

        self.shot_number = 0

        self.setup_ui()
        self.setup_zmq()
        self.setup_lhc()

    # ---------------- UI ----------------
    def setup_ui(self):

        label = QLabel("Shot number")
        self.shot_box = QSpinBox()
        self.shot_box.setRange(0, 1_000_000)
        self.shot_box.setValue(0)

        self.button = QPushButton("test trig")
        self.button.clicked.connect(self.trigger_shot)

        HOST_IP = sock.gethostbyname(sock.gethostname())

        self.pub_address = QLineEdit(f"tcp://{HOST_IP}:{PUB_PORT}")
        self.pub_address.setReadOnly(True)

        self.lhc_address = QLineEdit(f"tcp://{HOST_IP}:7892")
        self.lhc_address.setReadOnly(True)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("PUB"))
        layout.addWidget(self.pub_address)

        layout.addWidget(QLabel("LHC"))
        layout.addWidget(self.lhc_address)

        h = QHBoxLayout()
        h.addWidget(label)
        h.addWidget(self.shot_box)

        layout.addLayout(h)
        layout.addWidget(self.button)

        self.setLayout(layout)

    # ---------------- ZMQ ----------------
    def setup_zmq(self):
        self.context = zmq.Context()

        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind(f"tcp://*:{PUB_PORT}")

        self.pub_socket.setsockopt(zmq.LINGER, 0)

        print(f"PUB ready on {PUB_PORT}")

        time.sleep(0.5)  # IMPORTANT

    # ---------------- LHC ----------------
    def setup_lhc(self):
        self.server_lhc = ServerLHC(
            name="Dummy Shot Server",
            address=LHC_ADDRESS,
            freedom=0,
            device=DEVICE_SHOT,
            data={}
        )
        self.server_lhc.start()
        self.server_lhc.set_data({"shot_number": self.shot_number})

    # ---------------- Trigger ----------------
    def trigger_shot(self):
        self.shot_number += 1
        self.shot_box.setValue(self.shot_number)

        self.publish()
        self.update_lhc()

    def publish(self):
        msg = {
            "number": self.shot_number,
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
        }

        self.pub_socket.send_string("SHOOT", zmq.SNDMORE)
        self.pub_socket.send_json(msg)

        print("SHOT:", self.shot_number)

    def update_lhc(self):
        self.server_lhc.set_data({
            "shot_number": self.shot_number,
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
        })

    def closeEvent(self, event):
        self.server_lhc.stop()
        self.pub_socket.close()
        self.context.term()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DummyShot()
    w.show()
    sys.exit(app.exec())