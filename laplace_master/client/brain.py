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
        
        # self.obj_spec_tcp = {}  # keys: tcp://ip:port
        # self.obj_spec_plain = {}  # keys: ip:port

        # for addr, keys in obj.items():
        #     full_addr = self.cm._normalize_address(addr)        # tcp://ip:port
        #     plain_addr = full_addr.split("://", 1)[1]           # ip:port

        #     self.obj_spec_tcp[full_addr] = keys
        #     self.obj_spec_plain[plain_addr] = keys

        normalized_obj = {}
        for addr, keys in obj.items():
            if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
                raise ValueError(
                    f"Invalid objective spec for {addr}. "
                    f"Expected list[str], got: {keys}"
                )
            
            full_addr = self.cm._normalize_address(addr)
            normalized_obj[full_addr] = keys

        self.obj_spec = normalized_obj
        # -----------------------------

        for sample in data["samples"]:
            self.queue.append(sample)

        self._next()



    def _next(self, next_in_queue: bool=False):
        if self.waiting or not (self.motor_control_enabled or next_in_queue):
            return
        
        if not self.queue:              # if there is nothing in the queue
            self._send_results()        # send the results
            return                      # get out of the function

        self.current = self.queue.popleft()
        self.waiting = True

        self.current_measurements = {}
        # obj_addresses = []
        # for add in self.obj_spec.keys():
        #     obj_addresses.append(self.cm._normalize_address(add))
        
        self.expected_sources = set(self.obj_spec.keys())
        # self.expected_sources = set(self.obj_spec_plain.keys())
        # self.expected_sources = set(obj_addresses)

        print(f"[Brain] Expected objective sources: {self.expected_sources}")
        print(f"[Brain] Current inputs: {self.current['inputs']}")

        self.cm.sample_point(self.current["inputs"])

        if not self.queue:          # if the queue is empty
            self._send_results()    # send results


    def on_measurement(self, address: str, data: dict):
        if not self.waiting:
            return

        if address not in self.obj_spec:
            return

        # if address not in self.obj_spec_plain:
        #     return

        # data is already the payload with objective values
        values = data
        if not isinstance(values, dict):
            return

        # if "://" in address:
        #     address = address.split("://", 1)[1]

        # Initialize storage
        self.current_measurements.setdefault(address, {})

        expected_keys = self.obj_spec[address]  # now just a list of objective names
        
        # expected_keys = self.obj_spec_plain[address]
        
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

        # payload = {"results": self.results}
        # print(f"[Brain] Sending final results to {self.opt_address}")

        # self.cm.send_opt(self.opt_address, payload)

        formatted_results = []

        for r in self.results:
            formatted_outputs = {}

            for addr, values in r["outputs"].items():
                # Convert tcp://ip:port -> ip:port
                if "://" in addr:
                    plain_addr = addr.split("://", 1)[1]
                else:
                    plain_addr = addr

                formatted_outputs[plain_addr] = values

            formatted_results.append({
                "inputs": r["inputs"],
                "outputs": formatted_outputs,
                "batch": r["batch"],
                "candidate": r["candidate"],
            })

        payload = {"results": formatted_results}
        self.cm.send_opt(self.opt_address, payload)


    def set_motor_control(self, enabled: bool):
        self.motor_control_enabled = enabled
        # try to continue if there is a pending queue
        if enabled:
            self._next()