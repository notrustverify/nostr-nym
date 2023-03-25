import sys
import time

from websocket import WebSocketAddressException

import nym

if __name__ == '__main__':

    # wait for nym-client to start
    print("Start nostr-nym proxy, waiting for nym-client to start")
    time.sleep(5)

    nym.Serve()



