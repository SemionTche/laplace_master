# libraries
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QHBoxLayout, 
    QFileDialog, QLabel
)
from PyQt6.QtCore import Qt

class SaveBar(QWidget):
    '''
    Class made to define a QWidget used to group every elements of the saving path.
    The Entry contain the path where the data will be stored.
    '''
    def __init__(self, path: str | None = None):
        '''
        Initialization of the SaveBar class.
        
            Arg:
                path: (str, optional)
                    the path that should be set in the Entry.
        '''
        
        super().__init__() # heritage from QWidget

        # main layout
        path_layout = QHBoxLayout()
        self.setLayout(path_layout)

        # label
        save_label = QLabel("Saving path:")

        # entry
        self.save_entry = QLineEdit()
        self.save_entry.setPlaceholderText("Path to save data")
        self.save_entry.setMaximumWidth(800)
        self.save_entry.setFocusPolicy(Qt.FocusPolicy.ClickFocus) # focus only if the item is clicked

        # button
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.select_save_path)

        # add the items to the layout
        path_layout.addWidget(save_label)
        path_layout.addWidget(self.save_entry)
        path_layout.addWidget(browse_button)

        path_layout.setStretch(0, 0)  # Label stays compact
        path_layout.setStretch(1, 1)  # QLineEdit grows
        path_layout.setStretch(2, 0)  # Button stays compact

        if path is not None:        # if there is an initial path
             self.set_path(path)    # set the entry

    
    @property
    def saving_path(self) -> str:
        '''
        Helper to access to the path where the data should be saved.
        '''
        return self.save_entry.text().strip()
    
    def set_path(self, path: str) -> None:
        '''
        Set the saving entry with the given path.
        '''
        self.save_entry.setText(path)

    def select_save_path(self) -> None:
        '''
        Select the path from the directory window.
        '''
        # Open directory selection dialog
        directory = QFileDialog.getExistingDirectory(self, 
                                                     "Select directory to save data")
        
        if directory: # if a folder has been choosen
            self.save_entry.setText(directory)