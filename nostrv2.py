import asyncio
import json
import logging
from queue import Queue
import websockets
from websocket_server import WebsocketServer

logging.basicConfig(level=logging.INFO)


class Serve:

    def __init__(self):
        PORT = 9001

        print("nostr init")
        self.server = WebsocketServer(port=PORT)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)
        self.queue = Queue()
        self.server.run_forever()

    def newSurbsClient(self, clientid, surb):
        # Writing to file
        with open("client-surb", "a") as file1:
            # Writing data to a file
            file1.write(f"{clientid}:{surb}\n")

    # Called for every client connecting (after handshake)
    def new_client(self, client, server):
        print("New client connected and was given id %d" % client['id'])
        # self.server.send_message_to_all("Hey all, a new client has joined us")
        # self.server.send_message(client,f"Hey {client['id']}")

    # Called for every client disconnecting
    def client_left(self, client, server):
        print("Client(%d) disconnected" % client['id'])

    async def nostrMessage(self, client, message):
        data = json.loads(message)
        self.newSurbsClient(client['id'], data['senderTag'])

        # Stablishes a connection / intantes the client.
        # The client is actually an awaiting function that yields an
        # object which can then be used to send and receive messages.

        async with websockets.connect('ws://127.0.0.1:7000') as ws:
            # Sends a message.
            await ws.send(data['data'])

            answer = await ws.recv()
            print(type(answer))
            self.server.send_message(client, answer)
        # Closes the connection.

            #await websocket.close()



    # Called when a client sends a message
    def message_received(self, client, server, message):
        print("Client(%d) said: %s" % (client['id'], message))

        dataSend = asyncio.run(self.nostrMessage(client, message))


if __name__ == "__main__":
    nostr = Serve()
