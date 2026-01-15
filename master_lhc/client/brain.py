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
        self.cm: ClientManager = client_manager

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
        if not (data.get("is_init") or data.get("is_opt")):
            return

        self.queue.clear()
        self.results.clear()
        self.current = None
        self.waiting = False

        self.opt_address = opt_address

        # --- STRICT objective spec ---
        obj = data.get("obj")
        if not isinstance(obj, dict):
            raise ValueError("Objective spec must be a dict {address: [objective_names]}")

        for addr, keys in obj.items():
            if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
                raise ValueError(
                    f"Invalid objective spec for {addr}. "
                    "Expected list[str], got: {keys}"
                )

        self.obj_spec = obj
        # -----------------------------

        for sample in data["samples"]:
            self.queue.append(sample)

        self._next()



    def _next(self):
        if self.waiting or not self.motor_control_enabled:
            return

        if not self.queue:
            self._send_results()
            return

        self.current = self.queue.popleft()
        self.waiting = True

        self.current_measurements = {}
        self.expected_sources = set(self.obj_spec.keys())

        print(f"[Brain] Expected objective sources: {self.expected_sources}")
        print(f"[Brain] Current inputs: {self.current['inputs']}")

        self.cm.sample_point(self.current["inputs"])


    def on_measurement(self, address: str, data: dict):
        if not self.waiting:
            return

        if address not in self.obj_spec:
            return

        # data is already the payload with objective values
        values = data
        if not isinstance(values, dict):
            return

        # Initialize storage
        self.current_measurements.setdefault(address, {})

        expected_keys = self.obj_spec[address]  # now just a list of objective names

        for k in expected_keys:
            if k in values:
                self.current_measurements[address][k] = values[k]

        # Check completion for this address
        if len(self.current_measurements[address]) == len(expected_keys):
            self.expected_sources.discard(address)

        # Finalize sample if everything is collected
        if not self.expected_sources:
            self._finalize_current_sample()



    def _finalize_current_sample(self):
        self.results.append({
            "inputs": self.current["inputs"],
            "outputs": self.current_measurements,
            "batch": self.current["batch"],
            "candidate": self.current["candidate"],
        })

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