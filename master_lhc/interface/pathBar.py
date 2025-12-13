from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt

class PathBar(QWidget):

    def __init__(self, path: str | None = None):
        super().__init__()

        self.setMaximumWidth(1000)

        # Main layout
        path_layout = QHBoxLayout()
        self.setLayout(path_layout)

        self.save_entry = QLineEdit()
        self.save_entry.setPlaceholderText("Path to save data")
        self.save_entry.setMaximumWidth(800)
        self.save_entry.setFocusPolicy(Qt.FocusPolicy.ClickFocus) # focus only if the item is clicked

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.select_save_path)

        path_layout.addWidget(self.save_entry)
        path_layout.addWidget(browse_button)

        path_layout.setStretch(0, 1)  # QLineEdit grows
        path_layout.setStretch(1, 0)  # Button stays compact

        if path is not None:
             self.set_path(path)
    
    @property
    def path_to_save(self):
        return self.save_entry.text()
    
    def set_path(self, path: str):
        self.save_entry.setText(path)

    def select_save_path(self):
            # Open directory selection dialog
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select directory to save data"
            )
            if directory:
                self.save_entry.setText(directory)
                print(self.path_to_save)