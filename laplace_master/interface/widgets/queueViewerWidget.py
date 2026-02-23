# libraries
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit
)
from PyQt6.QtCore import pyqtSignal


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
        self.queue = [dict(s, outputs=obj_spec) for s in suggestions] # attach outputs to each suggestion
        self.current_index = 0
        self.update_display()
        self.update_buttons()

    def update_display(self) -> None:
        '''Update the text display for the current suggestion.'''
        if not self.queue:
            self.text_display.setText("<empty queue>")
            self.label_index.setText("0 / 0")
            return

        item = self.queue[self.current_index]
        text_lines = ["<b>Inputs:</b>"]
        for ip, positions in item.get("inputs", {}).items():
            text_lines.append(f"{ip}: {positions}")

        text_lines.append("<b>Outputs:</b>")
        for ip, keys in item.get("outputs", {}).items():
            text_lines.append(f"{ip}: {list(keys)}")  # just keys

        self.text_display.setHtml("<br>".join(text_lines))
        self.label_index.setText(f"{self.current_index + 1} / {len(self.queue)}")

    def update_buttons(self) -> None:
        '''Enable/disable navigation buttons depending on queue state.'''
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < len(self.queue) - 1)
        self.delete_btn.setEnabled(bool(self.queue))

    def on_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
            self.update_buttons()

    def on_next(self):
        if self.current_index < len(self.queue) - 1:
            self.current_index += 1
            self.update_display()
            self.update_buttons()

    def on_delete(self):
        if self.queue:
            self.queue.pop(self.current_index)
            self.delete_current.emit(self.current_index)
            if self.current_index >= len(self.queue):
                self.current_index = max(0, len(self.queue) - 1)
            self.update_display()
            self.update_buttons()