import time
from server_lhc.serverLHC import ServerLHC


if __name__ == "__main__":

    address = f"tcp://*:0004"
    data = {"hello": "world", "positions": [42., 63.], "unit": "mm"}

    server = ServerLHC(address=address, freedom=2, device="MOTOR", data=data, name="motor 2")
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()