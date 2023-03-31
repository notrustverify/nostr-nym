import asyncio
import datetime
import time
import json
import signal
import sys
import uuid
import websockets
from binascii import unhexlify, hexlify
from nostr import bech32
import argparse
from signal import SIGINT, SIGTERM
from websocket import WebSocketConnectionClosedException, WebSocketTimeoutException

import nym
from nostr.key import PrivateKey
from nostr.event import Event, EventKind
from nostr.key import PublicKey
from nostr.filter import Filter, Filters
from nostr.message_type import ClientMessageType


# From https://github.com/jeffthibault/python-nostr/blob/main/nostr/event.py
def note_id(noteHexId):
    converted_bits = bech32.convertbits(bytes.fromhex(noteHexId), 8, 5)
    return bech32.bech32_encode("note", converted_bits, bech32.Encoding.BECH32)


def getNostrPayload(received_message):
    try:
        payload = json.loads(received_message)['message']
        return json.loads(payload)
    except (UnicodeDecodeError, json.decoder.JSONDecodeError) as e:
        if DEBUG:
            print(f"Error parsing message {received_message}, error {e}")
        return None


def parseNewEvent(received_message):
    answer = getNostrPayload(received_message)
    if answer is None:
        return

    try:
        if answer[0] == "EOSE":
            return "EOSE"
        else:
            newEventData = answer[2]

    except IndexError as e:
        if DEBUG:
            print(f"Error parsing message {answer}, error {e}")
        return None

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


def parseNymMessage(received_message):
    answer = getNostrPayload(received_message)

    if answer is not None:
        if answer[0] == "OK":
            print(f"\n✅ Note successfully published with id {note_id(answer[1])}")
            return True
        else:
            print(f"Error with note: {answer}")
            return True
    return False



async def signalingMsg(msg, nymClientURI, waitForAnswer=False):
    async with websockets.connect(nymClientURI) as websocket:
        await websocket.send(msg)
        print("quit")

        try:
            if waitForAnswer:
                await websocket.recv()
                # print(response)
        except asyncio.IncompleteReadError as e:
            pass
        except (WebSocketConnectionClosedException, WebSocketTimeoutException) as e:
            print(f"websocket error: {e}")
        except RuntimeError:
            pass

        await websocket.close()


async def publish(msg, nymClientURI, relay):
    async with websockets.connect(nymClientURI) as websocket:
        await websocket.send(msg)

        # if nym-client close and some message was received, it's possible that there's some message send,
        # so using this quick and dirty loop to clean the messages
        while True:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=45)
                if parseNymMessage(msg):
                    break
                if DEBUG:
                    print(f"message left in ws: {msg}")

            except asyncio.exceptions.TimeoutError:
                print(f"Timeout")
                break

        await websocket.send(nym.Serve.createPayload(relay, "quit", padding=False))

        try:
            await asyncio.wait_for(websocket.recv(), timeout=2)
        except asyncio.exceptions.TimeoutError:
            pass
        finally:
            await websocket.close()


async def subscribe(msg, nymClientURI, relay, runForever=False):
    async with websockets.connect(nymClientURI) as websocket:
        await websocket.send(msg)

        while True:
            try:
                response = await websocket.recv()
                parsedEvent = parseNewEvent(response)

                if parsedEvent == "EOSE" and runForever:
                    await websocket.send(nym.Serve.createPayload(relay, "quit", padding=False))
                    print(f"\nall events received")
                    break
                elif parsedEvent == "EOSE":
                    print(f"\nall events received, waiting for new one")

            except asyncio.IncompleteReadError as e:
                pass
            except (WebSocketConnectionClosedException, WebSocketTimeoutException) as e:
                print(f"websocket error: {e}")
                continue
            # not a good way to do, for demo it's ok
            except:
                await websocket.send(nym.Serve.createPayload(relay, "quit", padding=False))

                try:
                    await asyncio.wait_for(websocket.recv(), timeout=2)
                except asyncio.exceptions.TimeoutError:
                    pass
                
                await websocket.close()
                break

        await websocket.close()


def newTextNote(privateKey, message, tags=None):
    if tags is None:
        tags = []
    pk = PrivateKey(unhexlify(privateKey))

    msg = message

    event_kind = EventKind.TEXT_NOTE
    event = Event(pk.public_key.hex(), content=msg, kind=event_kind, tags=tags)
    pk.sign_event(event)

    return event


async def main():
    parser = argparse.ArgumentParser(description='Light Nostr client')
    parser.add_argument('--cmd', dest='command', type=str, help='text-note | subscribe | filter', required=True)

    parser.add_argument('--pk', dest='privateKey', type=str, help='Private key in hex to sign message')
    parser.add_argument('--relay', dest='relay', type=str,
                        help='Service provider id (nym-client id) to interact with',
                        required=True)
    
    parser.add_argument('--message', dest='message', type=str, help='Message content')
    parser.add_argument('--req', dest='req', type=str, help='Search term for event')
    parser.add_argument('--limit', dest='limit', type=int, help='Subscription limit event', default=100)
    parser.add_argument('--author', dest='author', type=str, help='Author', default="npub1nftkhktqglvcsj5n4wetkpzxpy4e5x78wwj9y9p70ar9u5u8wh6qsxmzqs")
    parser.add_argument('--kinds', dest='kinds', type=int, help='Event kind', default=1)
    parser.add_argument('--since', dest='since', type=str, help='since timestamp')
    parser.add_argument('--nym-client,', dest='nymClient', type=str, help='URI of local nym-client',
                        default='ws://127.0.0.1:1977')
    parser.add_argument('--debug', dest="debug", type=bool, help="Debug enabled", default=False)

    args = parser.parse_args()

    global DEBUG
    DEBUG = args.debug
    command = args.command
    relay = args.relay
    nymClient = args.nymClient

    try:
        loop = asyncio.get_event_loop()

        if command == "text-note":

            privateKey = args.privateKey
            if privateKey is None:
                print("\nNo private key set, will generate one: ")
                rndPk = PrivateKey()
                privateKey = rndPk.hex()
                print(f"{rndPk.bech32()}\n{rndPk.public_key.bech32()}")
            else:
                privateKey = PrivateKey.from_nsec(privateKey).hex()

            message = args.message
            if message is None:
                message = "This is a note published trough Nym mixnet, visit https://nymtech.net for more information"

            event = newTextNote(privateKey, message)

            print(f"\nTry to publish event\n 📜 message: {event.content}\n 🪝 kind {event.kind}\n 📨 to {relay}")
            pub = loop.create_task(
                publish(nym.Serve.createPayload(relay, event.to_message(), padding=False), nymClient, relay))
            await pub

        elif command == "subscribe":

            filters = Filters([Filter(kinds=[EventKind.TEXT_NOTE], limit=args.limit)])
            subscription_id = uuid.uuid1().hex[:9]
            request = [ClientMessageType.REQUEST, subscription_id]
            request.extend(filters.to_json_array())

            print(f"\n📟 Subscribe to new events with {request} using relay {relay}")

            sub = loop.create_task(
                subscribe(nym.Serve.createPayload(relay, json.dumps(request), padding=False), nymClient, relay))
            await sub

        elif command == "filter":
            kinds = args.kinds
            author = PublicKey.from_npub(args.author).hex()
            since = args.since
            limit = args.limit

            if since is not None:
                filters = Filters([Filter(authors=[author], since=since, limit=limit, kinds=[kinds])])
            else:
                filters = Filters([Filter(authors=[author], kinds=[kinds], limit=limit)])

            subscription_id = uuid.uuid1().hex[:9]
            request = [ClientMessageType.REQUEST, subscription_id]
            request.extend(filters.to_json_array())

            print(f"\n📟 Filter existing events with {request} query using relay {relay}")
            sub = loop.create_task(
                subscribe(nym.Serve.createPayload(relay, json.dumps(request), padding=False), nymClient, relay,
                          runForever=True))
            await sub

    except KeyboardInterrupt:
        pending_tasks = [
            task for task in asyncio.Task.all_tasks() if not task.done()
        ]
        loop.run_until_complete(asyncio.gather(*pending_tasks))
        loop.close()


if __name__ == '__main__':
    asyncio.run(main())
