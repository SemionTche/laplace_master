# libraries
from PyQt6.QtWidgets import QApplication
import sys

# project
from interface.masterWindow import MasterWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterWindow() # initialize the window
    window.show()           # run the main loop
    sys.exit(app.exec())    # if the app terminated, end the process