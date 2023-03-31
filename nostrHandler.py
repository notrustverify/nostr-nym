import json
import sys
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


class NostrHandler:

    @staticmethod
    def createPayload(recipient, reply_message, senderTag=None, is_text=True, padding=False):
        messageToSend = ""
        if is_text and padding:
            headers = HEADER_APPLICATION_JSON
            padding = (NYM_KIND_TEXT + NYM_HEADER_SIZE_TEXT + HEADER_APPLICATION_JSON_BYTE).decode('utf-8')
            messageToSend = padding + headers + json.dumps(reply_message)
        elif not padding:
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

    def __init__(self, senderTag, eventQueue, nymWsHandler, padding=True):
        self.firstRun = True

        self.eventQueue = eventQueue

        self.senderTag = senderTag
        self.wsReady = False
        self.nymWsHandler = nymWsHandler
        self.padding = padding

        self.url = f"{utils.NOSTR_RELAY_URI_PORT}"
        websocketNostr.enableTrace(False)
        self.wsNostr = websocketNostr.WebSocketApp(self.url,
                                                   on_message=lambda ws, msg: self.on_message(
                                                       ws, msg),
                                                   on_error=lambda ws, msg: self.on_error(
                                                       ws, msg),
                                                   on_close=lambda ws, close_status_code, close_msg: self.on_close(
                                                       ws, close_status_code, close_msg),
                                                   on_open=lambda ws: self.on_open(ws),
                                                   )

        threading.Thread(target=self.eventHandler, daemon=True).start()

        # Set dispatcher to automatic reconnection
        self.wsNostr.run_forever(ping_interval=30, ping_timeout=10)

        self.wsNostr.close()

    def on_message(self, ws, message):
        if utils.DEBUG:
            print(message)

        self.nymWsHandler.send(NostrHandler.createPayload(None, message, self.senderTag, padding=self.padding))

    def on_close(self, ws, close_status_code, close_msg):
        print(f"Connection with {self.senderTag} closed")

        try:
            self.nymWsHandler.send(NostrHandler.createPayload(None, "ok", self.senderTag, padding=self.padding))
            self.wsNostr.close()
            sys.exit()
        except SystemExit:
            pass
        except:
            print(f"Error closing ws for {self.senderTag}")
            traceback.print_exc()


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
        print(f"Websocket started. Connected to {self.url}")
        self.wsReady = True

    def eventHandler(self):
        print("Interprocess communication started")
        while True:
            msg = self.eventQueue.get()
            print(f"Received event from client: {msg}")
            while not self.wsReady:
                pass

            if msg == "quit":
                self.wsNostr.close()
                sys.exit()

            self.wsNostr.send(msg)
