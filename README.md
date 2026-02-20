# Master

Master is a standalone GUI application designed to orchestrate experimental devices over a network.  
It connects to motor control systems, diagnostic devices, and an external optimizer using ZMQ servers built on the `laplace-server` protocol.

The application does not perform optimization itself.  
It acts as a supervisory layer that:

- Receives candidate suggestions from an optimizer
- Moves control systems accordingly
- Collects diagnostic measurements
- Sends structured results back to the optimizer

Master is intended to run on the same network as the devices while remaining fully decoupled from the hardware.

---

## Overview

Master provides a graphical interface to:

- Register remote servers by entering their address
- Automatically probe and identify device type
- Organize devices into logical panels
- Coordinate optimization-driven experiments

The system is modular and device-oriented. Each connected server declares its device type and capabilities, and Master routes it to the appropriate panel.

---

## Interface

The GUI is composed of several main sections:

### Server Bar

A top bar allows users to enter a server address.  
When validated, Master:

1. Verifies address format
2. Probes the server
3. Retrieves metadata (device type, name, degrees of freedom)

Depending on the detected device type, the server is placed in:

- **Control Systems Panel** (motors, gas systems)
- **Diagnostics Panel** (cameras)
- **Optimization Panel** (optimizer server)

Future extensions may include:
- A laser monitoring panel
- A global trigger / shot number server

---

### Save Bar

The save path can be configured from the GUI.  
When changed, a message is sent to all connected servers so they can update their saving path.

At the moment, Master does not handle data persistence itself.

---

### Optimization Panel

Master interacts with an external optimizer server.

The workflow is:

1. The optimizer sends a batch of suggested samples.
2. Master queues the suggestions.
3. If motor control is enabled (or manually triggered), Master:
   - Sends motor positions to control systems
   - Waits for diagnostic measurements
   - Aggregates the results
4. Once the batch is completed, results are sent back to the optimizer.

Master does not allow manual motor control.  
It is strictly an orchestration layer.

---

## Communication Model

Master communicates exclusively through ZMQ using the `laplace-server` protocol.

Each device runs as an independent server:
- Motors and gas systems expose control endpoints
- Cameras expose diagnostic data
- The optimizer exposes suggestion batches

Master connects as a client and routes messages internally based on device type.

This design ensures:
- Network decoupling from hardware
- Clear separation of responsibilities
- Scalability across multiple devices

---

## Project Structure (Simplified)

master/
│
├── client/
│   ├── clientManager.py
│   └── brain.py
│
├── interface/
│   ├── panels/
│   └── widgets/
│
├── main.py
└── config.ini

---

## Requirements

- Python 3.10+
- PyQt6
- ZeroMQ (pyzmq)
- `laplace-server` package
- `laplace-log` package

Install dependencies with:

```bash
pip install pyqt6 pyzmq qdarkstyle laplace-server laplace-log