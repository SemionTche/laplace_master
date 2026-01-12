from PyQt6.QtCore import QObject
from collections import deque

from client.clientManager import ClientManager

from PyQt6.QtCore import QObject
from collections import deque

class Brain(QObject):
    """
    Optimization controller.
    Owns the optimization loop and measured data.
    """

    def __init__(self, client_manager):
        super().__init__()
        self.cm = client_manager

        # FIFO queue of samples to evaluate
        self.queue = deque()

        # Collected results
        self.results = []

        # Currently evaluated sample
        self.current = None

        # True while waiting for a measurement
        self.waiting = False

        # Address of the OPT server (set dynamically)
        self.opt_address = None

        self.motor_control_enabled = False


    def on_opt_data(self, opt_address: str, data: dict):
        """
        Called when OPT server sends points to evaluate.
        """
        if not (data.get("is_init") or data.get("is_opt")):
            return

        # Reset state
        self.queue.clear()
        self.results.clear()
        self.current = None
        self.waiting = False

        # Remember OPT server address
        self.opt_address = opt_address

        # Load new samples
        for sample in data["samples"]:
            self.queue.append(sample)

        # Start loop
        self._next()


    def _next(self):
        '''
        Execute the next optimization sample if possible.
        '''
        # Do nothing if already waiting for a measurement
        if self.waiting:
            return

        # Do nothing if motor control is disabled
        if not self.motor_control_enabled:
            return

        # If no more samples, send results back to optimizer
        if not self.queue:
            print("[Brain] Optimization queue empty. Final results:")
            for r in self.results:
                print(r)  # print each result
            self._send_results()
            return

        # Pop next sample
        self.current = self.queue.popleft()
        self.waiting = True

        # Ask ClientManager to move and sample
        self.cm.sample_point(self.current["inputs"])




    def on_measurement(self, address: str, data: dict):
        """
        Called when a measurement arrives (e.g. from camera).
        """
        if not self.waiting:
            return

        if "value" not in data:
            return

        # Store result
        self.results.append({
            "inputs": self.current["inputs"],
            "output": data["value"],
            "batch": self.current["batch"],
            "candidate": self.current["candidate"],
        })

        # Ready for next point
        self.current = None
        self.waiting = False

        self._next()


    def _send_results(self):
        """
        Send all collected results back to OPT server.
        """
        if self.opt_address is None:
            return

        payload = {"results": self.results}
        print(f"[Brain] Sending final results to {self.opt_address}")

        self.cm.send_opt(self.opt_address, payload)

    def set_motor_control(self, enabled: bool):
        self.motor_control_enabled = enabled
        # try to continue if there is a pending queue
        if enabled:
            self._next()