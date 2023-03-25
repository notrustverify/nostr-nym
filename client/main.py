import asyncio
import datetime
import json
import sys

import websockets
from binascii import unhexlify, hexlify
from nostr import bech32
import argparse
import nym
from nostr.key import PrivateKey, PublicKey
from nostr.event import Event, EventKind
from nostr.subscription import Subscription
from nostr.bech32 import Encoding, bech32_encode
from nostr.key import PublicKey


# From https://github.com/jeffthibault/python-nostr/blob/main/nostr/event.py
def note_id(noteHexId):
    converted_bits = bech32.convertbits(bytes.fromhex(noteHexId), 8, 5)
    return bech32.bech32_encode("note", converted_bits, bech32.Encoding.BECH32)


def getNostrPayload(received_message):
    try:
        payload = json.loads(received_message)['message'][54:]
        return json.loads(json.loads(payload))
    except (UnicodeDecodeError, json.decoder.JSONDecodeError) as e:
        print(f"Error parsing message {received_message}, error {e}")
        return None


def parseNewEvent(received_message):
    answer = getNostrPayload(received_message)
    if answer is None:
        return

    try:
        if answer[0] == "EOSE":
            print(f"\nall events received, waiting for new one")
            return
        else:
            newEventData = answer[2]
    except IndexError as e:
        print(f"Error parsing message {answer}, error {e}")
        return False

    noteid = newEventData['id']
    fromPub = newEventData['pubkey']
    createdAt = datetime.datetime.fromtimestamp(newEventData['created_at'])
    kind = newEventData['kind']
    tags = newEventData['tags']
    content = newEventData['content']
    sig = newEventData['sig']

    print(f"\n🚀 New Event received, note id: {note_id(noteid)}"
          f"\n\t 🔑 from: {PublicKey(unhexlify(fromPub)).bech32()}"
          f"\n\t ⏰ created at: {createdAt}"
          f"\n\t 🪝 kind: {kind}"
          f"\n\t 🏷️ tags: {tags}"
          f"\n\t 📜 content: {content}"
          f"\n\t 🖋️ signature: {sig[:21]}...")

    return True


def parseNymMessage(received_message):
    answer = getNostrPayload(received_message)
    if answer is not None:
        if answer[0] == "OK":
            print(f"\n✅ Note successfully published with id {note_id(answer[1])}")
        else:
            print(f"Error with note: {answer}")


async def publish(msg, nymClientURI):
    async with websockets.connect(nymClientURI) as websocket:
        await websocket.send(msg)

        msg = await websocket.recv()
        parseNymMessage(msg)

        await websocket.close()


async def subscribe(msg, nymClientURI):
    async with websockets.connect(nymClientURI) as websocket:
        await websocket.send(msg)

        while True:
            try:
                response = await websocket.recv()
                parseNewEvent(response)
            except (websocket.WebSocketConnectionClosedException, websocket.WebSocketTimeoutException) as e:
                print(f"websocket error: {e}")
            finally:
                websocket.close()





def newTextNote(relay, nymClientURI, privateKey, message, tags=[]):
    pk = PrivateKey(unhexlify(privateKey))

    msg = message

    event_kind = EventKind.TEXT_NOTE
    event = Event(pk.public_key.hex(), content=msg, kind=event_kind, tags=tags)
    pk.sign_event(event)

    print(f"\nTry to publish event\n 📜 message: {event.content}\n 🪝 kind {event.kind}\n 📨 to {relay}")
    asyncio.get_event_loop().run_until_complete(publish(nym.createPayload(relay, event.to_message()), nymClientURI))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Light Nostr client')
    parser.add_argument('--cmd', dest='command', type=str, help='text-note | subscribe', required=True)

    parser.add_argument('--pk', dest='privateKey', type=str, help='Private key in hex to sign message')
    parser.add_argument('--relay', dest='relay', type=str,
                        help='Service provider id (nym-client id) to interact with',
                        required=True)
    parser.add_argument('--message', dest='message', type=str, help='Message content')
    parser.add_argument('--limit', dest='limit', type=str, help='Subscription limit event', default=100)
    parser.add_argument('--nym-client,', dest='nymClient', type=str, help='URI of local nym-client',
                        default='ws://127.0.0.1:1977')
    args = parser.parse_args()

    command = args.command
    relay = args.relay
    nymClient = args.nymClient

    if command == "text-note":
        privateKey = args.privateKey

        if privateKey is None:
            print("\nNo private key set, will generate one: ")
            rndPk = PrivateKey()
            privateKey = rndPk.hex()
            print(f"{rndPk.bech32()}")

        message = args.message
        if message is None:
            message = "This is a note published trough Nym mixnet, visit https://nymtech.net for more information"

        newTextNote(relay, nymClient, privateKey, message)

    elif command == "subscribe":
        print(f"\n📟 Subscribe to new events using relay {relay} ")

        subscriptionReq = ["REQ", "RAND", {"limit": str({args.limit})}]

        asyncio.get_event_loop().run_until_complete(
            subscribe(nym.createPayload(relay, json.dumps(subscriptionReq)), nymClient))
