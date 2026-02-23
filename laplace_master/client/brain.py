# libraries
from PyQt6.QtCore import QObject, pyqtSignal
from laplace_log import log

# project
from client.clientManager import ClientManager
from utils.json_encoder import json_style
from utils.config_helper import get_from_config


class Brain(QObject):
    '''
    Central controller of the optimization workflow.

    The Brain coordinates optimization suggestions, motor commands,
    and diagnostic measurements. It manages the evaluation queue,
    synchronizes measurements from multiple sources, and returns
    aggregated results to the optimization server.
    '''
    queue_updated = pyqtSignal(list, dict)

    def __init__(self, client_manager: ClientManager):
        '''
        Initialize the Brain.

        Arg:
            client_manager: (ClientManager)
                Communication interface used to interact with control,
                diagnostic, and optimization servers.
        '''
        super().__init__()  # heritage from QObject
        
        self.client_manager = client_manager

        self.motor_control_enabled = False  # the right to move motors
        
        self.suggestions = []  # candidates suggested by the optimizer
        self.results = []      # collected results from the diagnostics
        self.obj_spec = {}

        self.current = None   # Currently evaluated sample
        self.waiting = False  # True while waiting for a measurement
        self.motion_pending = False  # doing a measurement (motors moving)

        self.opt_address = "Unknown"  # Address of the OPT server

        self.tolerance = get_from_config(
            module="opt",
            item="tolerance",
            default_value=1e-4,
            type=float)

        log.info("Brain loaded.")


    def on_opt_data(self, 
                    opt_address: str, 
                    data: dict) -> None:
        '''
        Handle incoming data from the optimization server.

        Resets the current state, stores the objective specification,
        loads new suggested samples into the queue, and starts the
        evaluation process if possible.

        Args:
            opt_address: (str)
                Address of the optimization server.
            
            data: (dict)
                Payload containing objective specification and samples.
        '''
        # if the received data is not an initialization or optimization suggestion
        if not (data.get("is_init") or data.get("is_opt")):
            return      # ignore it

        # reset the attributes
        self.suggestions.clear()
        self.results.clear()
        self.obj_spec.clear()
        self.current = None
        self.waiting = False
        log.info("The Brain suggestions were cleared.")
        self.queue_updated.emit(self.suggestions, self.obj_spec)

        # log.info("New optimization data received:\n"
        #         f"{json_style(data)}")

        self.opt_address = opt_address     # get the optimizer address
        obj: dict = data.get("obj", {})    # get the objective list of keys along each objective address

        normalized_obj = {}
        # verifie que le dictionnaire contient des listes et que ces listes contienent des strings
        for addr, keys in obj.items():
            if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
                raise ValueError(
                    f"Invalid objective spec for {addr}. "
                    f"Expected list[str], got: {keys}"
                )
            normalized_obj[addr] = keys

        self.obj_spec = normalized_obj

        # add samples to the suggestions
        for sample in data["samples"]:
            self.suggestions.append(sample)
        
        log.info("New optimization suggestions added:\n"
                 f"{json_style(self.suggestions)}")
        self.queue_updated.emit(self.suggestions, self.obj_spec)
        
        self._next()  # provide the next point to the control system


    def _next(self, next_in_queue: int | None=None) -> None:
        '''
        Start evaluation of the next suggested sample if allowed.

        A new sample is triggered only if the system is not already
        waiting for measurements and motor control is enabled
        (or explicitly forced via `next_in_queue`).
        '''
        # if we are waiting for a measure 
        if self.waiting:
            return         # don't look for the next suggestion

        if self.motion_pending:
            return

        # Do not proceed if motors are not enabled
        # unless we explicitly ask for an element in the suggestions
        if not (self.motor_control_enabled or next_in_queue is not None):
            return
        
        if not self.suggestions:                        # if there is no suggestion
            log.info("No suggestion available.")        # send the results
            return                                      # get out of the function

        if next_in_queue is None:
            next_in_queue = 0

        self.current = self.suggestions.pop(next_in_queue)  # get the current point to sample and pop it from the suggestions
        self.queue_updated.emit(self.suggestions, self.obj_spec)
        self.waiting = True                     # we start to wait for a measure
        self.motion_pending = True

        self.current_measurements = {}          # gather the measures
        self.expected_sources = set(self.obj_spec.keys())

        log.info("Measuring inputs:\n"
                 f"{json_style(self.current['inputs'])}")

        self.client_manager.sample_point(self.current["inputs"])  # send the imputs to control system servers

        # if not self.suggestions:    # if there is no suggestion
        #     self._send_results()    # send results


    def on_motor_position_update(self, address: str, positions: dict):
        if not self.waiting or not self.motion_pending:
            return

        target = self.current["inputs"]

        if self._motors_match_target(positions, target):
            log.info("Motors reached target. Starting measurement phase.")
            self.motion_pending = False


    def _motors_match_target(self, current, target):        
        current_positions = current.get("positions", [])

        for address, target_positions in target.items():
            if len(current_positions) != len(target_positions):
                return False

            for c, t in zip(current_positions, target_positions):
                if abs(c - t) > self.tolerance:
                    return False

        return True


    def on_measurement(self, 
                       address: str, 
                       data: dict) -> None:
        '''
        Process a measurement received from a diagnostic server.

        Measurements are collected until all expected sources have
        responded for the current sample. Once complete, the sample
        is finalized.

        Args:
            address: (str)
                Address of the diagnostic server.
            
            data: (dict)
                Measured values for the current sample.
        '''
        if not self.waiting:               # if we are not waiting for a measure
            return                         # we do not continue

        if self.motion_pending:
            return

        if address not in self.obj_spec:   # if a measure is received from an unexpected address
            return                         # ignore it

        values = data
        if not isinstance(values, dict):
            return
        
        log.info(
            f"Measurement received from {address}:\n"
            f"{json_style(values)}"
        )

        # Initialize storage
        self.current_measurements.setdefault(address, {})  # create a key with empty dict in current_measurements

        expected_keys = self.obj_spec[address]  # now just a list of objective names
        
        for k in expected_keys:
            if k in values:
                self.current_measurements[address][k] = values[k]

        # Check completion for this address
        if len(self.current_measurements[address]) == len(expected_keys):
            self.expected_sources.discard(address)

        # Finalize sample if everything is collected
        if not self.expected_sources:
            log.info("All diagnostic measurements collected. Finalizing sample.")
            self._finalize_current_sample()


    def _finalize_current_sample(self) -> None:
        '''
        Finalize the current sample once all measurements are collected.

        The aggregated inputs and outputs are stored. If additional
        suggestions remain, evaluation continues; otherwise results
        are sent back to the optimizer.
        '''
        if not isinstance(self.current, dict):
            return
        
        self.results.append({
            "inputs": self.current["inputs"],
            "outputs": self.current_measurements,
            "batch": self.current["batch"],
            "candidate": self.current["candidate"],
        })

        self.current = None
        self.waiting = False

        self.queue_updated.emit(self.suggestions, self.obj_spec)

        if self.suggestions:
            self._next()
        else:
            self._send_results()  # Batch finished


    def _send_results(self) -> None:
        '''
        Send collected batch results to the optimization server.
        '''
        if self.opt_address is None:
            return

        if self.results:
            payload = {"results": self.results}
            log.info(f"Sending results to optimizer: {self.opt_address}\n"
                    f"{json_style(payload)}")

            self.client_manager.send_opt(self.opt_address, payload)


    def set_motor_control(self, enabled: bool) -> None:
        '''
        Enable or disable motor control.

        When enabling control, the next queued sample is triggered
        if available.

        Arg:
            enabled : bool
                Whether motor movement is allowed.
        '''
        # set the motor control
        self.motor_control_enabled = enabled
        
        if enabled:         # if motors can be drive
            self._next()    # get the next sample
    

    def delete_suggestion(self, index: int):
        deleted = self.suggestions.pop(index)
        log.info(f"Suggestion deleted:\n{json_style(deleted)}")