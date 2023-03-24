import json
import threading
import traceback
import utils
import websocket as websocketNostr


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

class WebsocketHandler:

    @staticmethod
    def createPayload(recipient, reply_message, senderTag=None, is_text=True, nopadding=False):
        messageToSend = ""
        if is_text:
            headers = HEADER_APPLICATION_JSON
            padding = (NYM_KIND_TEXT + NYM_HEADER_SIZE_TEXT + HEADER_APPLICATION_JSON_BYTE).decode('utf-8')
            messageToSend = padding + headers + json.dumps(reply_message)
        elif nopadding:
            messageToSend = reply_message
        else:
            # not used now, to investigate later
            padding = (NYM_KIND_BINARY + NYM_HEADER_BINARY).decode('utf-8')

        dataToSend = {
            "type": "reply",
            # append \x00 because of "kind" message is non binary and equal 0 + 1 bytes because no header are set
            # "message": ,
            "message": messageToSend
        }

        if senderTag is not None:
            dataToSend.update({'senderTag': senderTag})
        elif recipient is not None:
            dataToSend.update({'recipient': recipient})
            print(dataToSend)

        return json.dumps(dataToSend)

    def __init__(self, senderTag, eventQueue,nymWsHandler):
        self.firstRun = True
        self.eventQueue = eventQueue
        self.senderTag = senderTag
        self.wsReady = False
        self.nymWsHandler = nymWsHandler

        url = f"{utils.NOSTR_RELAY_URI_PORT}"
        websocketNostr.enableTrace(False)
        self.wsNostr = websocketNostr.WebSocketApp(url,
                                                   on_message=lambda ws, msg: self.on_message(
                                             ws, msg),
                                                   on_error=lambda ws, msg: self.on_error(
                                             ws, msg),
                                                   on_close=lambda ws: self.on_close(
                                             ws),
                                                   on_open=lambda ws: self.on_open(ws),
                                                   )

        threading.Thread(target=self.eventHandler, daemon=True).start()

        # Set dispatcher to automatic reconnection
        self.wsNostr.run_forever(ping_interval=30, ping_timeout=10)

        self.wsNostr.close()

    def on_message(self, ws, message):
        self.nymWsHandler.send(WebsocketHandler.createPayload(None, message, self.senderTag))

    def on_close(self, ws):
        print(f"Connection to nym-client closed")

    def on_error(self, ws, message):
        try:
            print(f"Error ws: {message}")
            traceback.print_exc()
        except UnicodeDecodeError as e:
            print(f"Unicode error, nothing to do about: {e}")
            return
        finally:
            self.wsNostr.close()

    def on_open(self, ws):
        print("Websocket started")
        self.wsReady = True

    def eventHandler(self):
        print("Interprocess communication started")
        while True:
            msg = self.eventQueue.get()
            print(f"Received event from client: {msg}")
            while not self.wsReady:
                pass

            self.wsNostr.send(msg)