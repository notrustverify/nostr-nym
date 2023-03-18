import sys
import threading
from queue import Queue


threadEvent = threading.Event()   # define an Event


def startThreads():
    import nym
    import nostr

    nym = threading.Thread(target=nym.Serve, args=(queueRecvEvents, queueSendEvents,threadEvent))
    nostr = threading.Thread(target=nostr.Serve, args=(queueRecvEvents, queueSendEvents,threadEvent))

    nym.start()
    nostr.start()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    queueRecvEvents = Queue()
    queueSendEvents = Queue()

    nostrnym = threading.Thread(target=startThreads, daemon=True)
    nostrnym.start()

    threadEvent.wait()
