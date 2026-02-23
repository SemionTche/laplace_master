# libraries
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit
)
from PyQt6.QtCore import pyqtSignal
from laplace_log import log


class QueueViewerWidget(QWidget):
    '''
    Widget used to display and navigate optimization queue elements.

    Displays:
        - Current element index / total
        - Inputs (grouped by IP)
        - Outputs (grouped by IP and keys)

    Provides:
        - Navigate left/right
        - Delete current element
    '''

    # Signals (logic handled elsewhere)
    navigate_left = pyqtSignal()
    navigate_right = pyqtSignal()
    delete_current = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.queue = []          # full list of suggestions
        self.current_index = 0   # currently displayed element

        # Main layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Toolbar layout
        toolbar = QHBoxLayout()
        self.prev_btn = QPushButton("<")
        self.next_btn = QPushButton(">")
        self.delete_btn = QPushButton("Delete")
        self.label_index = QLabel("0 / 0")
        toolbar.addWidget(self.prev_btn)
        toolbar.addWidget(self.next_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.label_index)
        layout.addLayout(toolbar)

        # Text display for current suggestion
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)

        # Connect buttons
        self.prev_btn.clicked.connect(self.on_prev)
        self.next_btn.clicked.connect(self.on_next)
        self.delete_btn.clicked.connect(self.on_delete)

        self.update_buttons()


    def set_queue(self, suggestions: list, obj_spec: dict) -> None:
        '''Replace the queue with a new list of suggestions.'''
        # set the queue
        self.queue = [dict(s, outputs=obj_spec) for s in suggestions] # attach outputs to each suggestion
        self.current_index = 0
        
        # update the widget
        self.update_display()
        self.update_buttons()


    def update_display(self) -> None:
        '''Update the text display for the current suggestion.'''
        if not self.queue:                                  # if there is no element in the queue
            self.text_display.setText("<empty queue>")      # print it
            self.label_index.setText("0 / 0")               # adapt the counter
            return

        item = self.queue[self.current_index]                   # else get the current element in the queue
        text_lines = ["<b>Inputs:</b>"]
        for ip, positions in item.get("inputs", {}).items():
            text_lines.append(f"{ip}: {positions}")             # make one line per input ip

        text_lines.append("<b>Outputs:</b>")
        for ip, keys in item.get("outputs", {}).items():
            text_lines.append(f"{ip}: {list(keys)}")            # make one line per objective ip

        self.text_display.setHtml("<br>".join(text_lines))                          # update the displayed text
        self.label_index.setText(f"{self.current_index + 1} / {len(self.queue)}")   # update the index counter label 


    def update_buttons(self) -> None:
        '''Enable/disable navigation buttons depending on queue state.'''
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < len(self.queue) - 1)
        self.delete_btn.setEnabled(bool(self.queue))


    def on_prev(self):
        '''When previous is clicked'''
        if self.current_index > 0:
            log.debug("Previous in queue clicked.")
            self.current_index -= 1
            self.update_display()
            self.update_buttons()


    def on_next(self):
        '''When next is clicked.'''
        if self.current_index < len(self.queue) - 1:
            log.debug("Next in queue clicked.")
            self.current_index += 1
            self.update_display()
            self.update_buttons()


    def on_delete(self):
        '''When delete is clicked.'''
        if self.queue:
            log.debug("Delete from queue clicked.")
            self.queue.pop(self.current_index)
            self.delete_current.emit(self.current_index)
            if self.current_index >= len(self.queue):
                self.current_index = max(0, len(self.queue) - 1)
            self.update_display()
            self.update_buttons()