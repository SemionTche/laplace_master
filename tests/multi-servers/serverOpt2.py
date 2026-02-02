import time
from server_lhc.serverLHC import ServerLHC


if __name__ == "__main__":

    address = f"tcp://*:0006"
    data = {"hello": "world", "positions": [42.], "unit": "bar"}

    server = ServerLHC(address=address, freedom=0, device="OPT", data=data, name="opt 2")
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()