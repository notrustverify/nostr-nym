import base64
import json
import threading
import time

import websocket

from datetime import datetime
import traceback
import rel
import utils

self_address_request = json.dumps({
    "type": "selfAddress"
})

CMD_NEW_TEXT = "newText"
CMD_GET_TEXT = "getText"
CMD_GET_PING = "ping"

NYM_KIND_TEXT = b'\x00'  # uint8
NYM_KIND_BINARY = b'\x01'

NYM_HEADER_SIZE_TEXT = b'\x00' * 6  # set to 0 if it's a text
NYM_HEADER_BINARY = b'\x00' * 8  # not used now, to investigate later

HEADER_TEXT_PLAIN_BYTE = b")"
HEADER_APPLICATION_JSON_BYTE = b"."

# to modify, cleaner solution
HEADER_APPLICATION_JSON = "{\"mimeType\":\"application/json\",\"headers\":null}"
TOTAL_HEADERS_PAD_SIZE = len(HEADER_APPLICATION_JSON) + len(NYM_HEADER_SIZE_TEXT) + len(
    HEADER_APPLICATION_JSON_BYTE) + 1


class Serve:

    @staticmethod
    def createPayload(recipient, reply_message, senderTag=None, is_text=True):
        if is_text:
            headers = HEADER_APPLICATION_JSON
            padding = (NYM_KIND_TEXT + NYM_HEADER_SIZE_TEXT + HEADER_APPLICATION_JSON_BYTE).decode('utf-8')
        else:
            # not used now, to investigate later
            padding = (NYM_KIND_BINARY + NYM_HEADER_BINARY).decode('utf-8')

        dataToSend = {
            "type": "reply",
            # append \x00 because of "kind" message is non binary and equal 0 + 1 bytes because no header are set
            # "message": ,
            "message": padding + headers + reply_message
        }

        if senderTag is not None:
            dataToSend.update({'senderTag': senderTag})
        elif recipient is not None:
            dataToSend.update({'recipient': recipient})

        return json.dumps(dataToSend)

    def __init__(self, queueRecvEvents, queueSendEvents, threadEvent):
        url = f"ws://{utils.NOSTR_RELAY_ADDR}:{utils.NOSTR_RELAY_PORT}"
        self.firstRun = True
        self.queueRecvEvents = queueRecvEvents
        self.queueSendEvents = queueSendEvents
        self.threadEvent = threadEvent

        websocket.enableTrace(False)
        eventRecv = threading.Thread(target=self.queueConsumer)
        eventRecv.start()

        self.ws = websocket.WebSocketApp(url,
                                         on_message=lambda ws, msg: self.on_message(
                                             ws, msg),
                                         on_error=lambda ws, msg: self.on_error(
                                             ws, msg),
                                         on_close=lambda ws: self.on_close(
                                             ws),
                                         on_open=lambda ws: self.on_open(ws),
                                         on_pong=lambda ws, msg: self.on_pong(ws, msg)
                                         )

        # Set dispatcher to automatic reconnection

        self.ws.run_forever(ping_interval=2, ping_timeout=1)

        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()
        self.ws.close()

    def queueConsumer(self):
        while True:
            event = self.queueRecvEvents.get()
            print(f"New event recv: {event}")

            self.ws.send(event['data'])
            time.sleep(0.1)

    def on_pong(self, ws, msg):
        #ws.send(self_address_request)
        pass

    def on_open(self, ws):
        print("Nostr relay connected")
        #self.ws.send('["REQ", "RAND", {"limit": 2}]')


    def on_error(self, ws, message):
        try:
            print(f"Error ws: {message}")
            traceback.print_exc()
        except UnicodeDecodeError as e:
            print(f"Unicode error, nothing to do about: {e}")
            return
        finally:
            self.ws.close()
            self.threadEvent.set()

    def on_close(self, ws):
        self.ws.close()
        print(f"Connection to nostr closed")

    def on_message(self, ws, message):
        print(f"Send event: {message}")
        self.queueSendEvents.put({'data': message,'senderTag': "E1Uf8XqwF9gb6CnauD7q22"})

