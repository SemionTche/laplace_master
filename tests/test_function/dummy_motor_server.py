import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QDoubleSpinBox,
    QFormLayout,
)

from laplace_server.server_lhc import ServerLHC
from laplace_server.protocol import DEVICE_MOTOR


ADDRESS = "tcp://*:5555"


class DummyMotor:
    def __init__(self):
        self.positions = [0.0, 0.0]

    def set_positions(self, positions):
        print(f"[Motor] Moving to {positions}")

        self.positions[0] = float(positions["0"])
        self.positions[1] = float(positions["1"])

        print(f"[Motor] New positions = {self.positions}")

    def get_data(self):
        return {
            "positions": self.positions,
            "unit": "a.u."
        }


class DummyMotorWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dummy Motor")

        self.motor = DummyMotor()

        self.server = ServerLHC(
            address=ADDRESS,
            freedom=2,
            device=DEVICE_MOTOR,
            data=self.motor.get_data(),
            name="dummy_motor"
        )

        self.server.set_name_list(["Direction x", "Direction Y"])
        self.server.set_on_position_changed(self.on_position_changed)

        self.init_ui()
        self.server.start()


    def init_ui(self):
        layout = QVBoxLayout()

        # Address display
        layout.addWidget(QLabel("Server address:"))

        self.address_entry = QLineEdit(
            self.server.address_for_client
        )
        self.address_entry.setReadOnly(True)

        layout.addWidget(self.address_entry)

        # Motor values
        form = QFormLayout()

        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(-1e6, 1e6)
        self.spin_x.setDecimals(6)

        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(-1e6, 1e6)
        self.spin_y.setDecimals(6)

        form.addRow("Direction x:", self.spin_x)
        form.addRow("Direction y:", self.spin_y)

        layout.addLayout(form)

        self.setLayout(layout)


    def on_position_changed(self, positions):
        """
        Called when master sends new motor targets.
        """
        self.motor.set_positions(positions)

        self.server.set_data(
            self.motor.get_data()
        )

        # Update GUI
        self.spin_x.setValue(
            self.motor.positions[0]
        )
        self.spin_y.setValue(
            self.motor.positions[1]
        )


    def closeEvent(self, event):
        self.server.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DummyMotorWindow()
    window.resize(350, 150)
    window.show()

    sys.exit(app.exec())