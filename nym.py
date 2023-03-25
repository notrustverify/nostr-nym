import json
import queue
import sys

import websocket
import traceback
import rel
from websocket import WebSocketAddressException

import utils
import threading
import nostrHandler

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

    def __init__(self):
        url = f"{utils.NYM_CLIENT_URI}"
        self.firstRun = True
        self.clientQueues = {}
        self.url = url
        websocket.enableTrace(False)

        self.ws = websocket.WebSocketApp(self.url,
                                         on_message=lambda ws, msg: self.on_message(
                                             ws, msg),
                                         on_error=lambda ws, msg: self.on_error(
                                             ws, msg),
                                         on_close=lambda ws, close_status_code, close_msg: self.on_close(ws,
                                                                                                         close_status_code,
                                                                                                         close_msg),
                                         on_open=lambda ws: self.on_open(ws),
                                         # on_pong=lambda ws, msg: self.on_pong(ws, msg)
                                         )

        # Set dispatcher to automatic reconnection
        self.ws.run_forever()

        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()
        self.ws.close()

    def on_pong(self, ws, msg):
        ws.send(self_address_request)

    def on_open(self, ws):
        self.ws.send(self_address_request)

    def on_error(self, ws, message):
        try:
            print(f"Error ws: {message}")

            if type(message) == WebSocketAddressException:
                print(f"nym-client {self.url} is not accessible, quit")
                raise ValueError(WebSocketAddressException)

            if type(message) == UnicodeDecodeError:
                return

        except UnicodeDecodeError as e:
            print(f"Unicode error, nothing to do about: {e}")
            return
        except:
            traceback.print_exc()
            self.ws.close()
            sys.exit(1)

    def on_close(self, ws, close_status_code, close_msg):
        print(f"Connection to nym-client closed, close_status_code {close_status_code}, close_msg {close_msg}")
        sys.exit()

    def on_message(self, ws, message):
        try:
            if self.firstRun:
                self_address = json.loads(message)
                print("Our address is: {}".format(self_address["address"]))
                self.firstRun = False
                return

            received_message = json.loads(message)

            # test if it's ping answer message
            if received_message.get('address'):
                return

            recipient = None

        except UnicodeDecodeError as e:
            print(f"Unicode error, nothing to do about: {e}")
            return

        try:
            kindReceived = bytes(received_message['message'][0:8], 'utf-8')[0:1]
        except IndexError as e:
            print(f"Error getting message kind, {e}")
            traceback.print_exc()
            return

        # we received the data in a json
        try:
            # received data with padding, start at the 54th bytes
            payload = received_message['message'][TOTAL_HEADERS_PAD_SIZE:]

            if kindReceived == NYM_KIND_TEXT:
                received_data = json.loads(payload)
            elif kindReceived == NYM_KIND_BINARY:
                print("bin data received. Don't know what to do")
                return
            else:
                print(message)
                print("no message kind received. Don't know what to do")
                received_data = received_message['message']
                print(received_data)

            senderTag = received_message.get('senderTag', None)

            if senderTag is None:
                recipient = received_data['sender']
            else:
                recipient = None

            if utils.DEBUG:
                print(f"-> Got {received_message}")
            else:
                print(f"-> Got message from {senderTag}")

            self.manageClient(senderTag, received_data)

        except (IndexError, KeyError, json.JSONDecodeError) as e:
            traceback.print_exc()

            if recipient is not None or senderTag is not None:
                err_msg = f"Error parsing message: {e}"
                reply_message = err_msg
                self.ws.send(Serve.createPayload(recipient, reply_message, senderTag))
                print(f"send error message, data received {message}")
                return
            else:
                print(f"No recipient found in message {received_message}")
                return None

    def manageClient(self, senderTag, event):
        if self.clientQueues.get(senderTag):
            print(f"Put message to queue {senderTag}")
            self.clientQueues[senderTag].put(event)
        else:
            print(f"Create queue for {senderTag}")
            self.createQueueClient(senderTag)
            print(f"Start thread")
            threading.Thread(target=nostrHandler.NostrHandler,
                             args=(senderTag, self.clientQueues[senderTag], self.ws,),
                             daemon=True).start()
            print(self.clientQueues)
            self.clientQueues[senderTag].put(event)

    def createQueueClient(self, senderTag):
        self.clientQueues.update({senderTag: queue.Queue()})


if __name__ == '__main__':
    Serve()
