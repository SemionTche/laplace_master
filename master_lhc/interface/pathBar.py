from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QHBoxLayout, QFileDialog
)

class PathBar(QWidget):

    def __init__(self):
        super().__init__()

        # Main layout
        path_layout = QHBoxLayout()
        self.setLayout(path_layout)

        self.save_entry = QLineEdit()
        self.save_entry.setPlaceholderText("Path to save data")

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.select_save_path)

        path_layout.addWidget(self.save_entry)
        path_layout.addWidget(browse_button)
    
    @property
    def path_to_save(self):
        return self.save_entry.text()

    def select_save_path(self):
            # Open directory selection dialog
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select directory to save data"
            )
            if directory:
                self.save_entry.setText(directory)
                print(self.path_to_save)