# Nostr-nym client

This client is for demo purpose, it can post events and subscribe to them on [Nostr protocol](https://nostr.how/)

## Installation

Requirements:
* python
* pipenv, can be installed with `pip install pipenv`
* [nym-client](https://github.com/nymtech/nym/releases) can be found under `Nym Binaries v...`

### Nym-client

```bash

# init the nym-client
./nym-client init --id nostr-client

# start the nym-client
./nym-client run --id nostr-client

```

### Nostr client

```bash
git clone https://github.com/notrustverify/nostr-nym.git
cd client
pipenv shell && pipenv install
```

## Usage

A public relay is available at `2gc9QidpXs4YGKmphinsDhWTHxdy2TZgWYWz2VenN5jL.dkwwJqS1zXa9BuPAFdniRN2HxFvAbTybAmrUHGAT5KV@2BuMSfMW3zpeAjKXyKLhmY4QW1DXurrtSPEJ6CjX3SEh`


Start the nym-client `./nym-client run --id nostr-client`

### Global argurments

| *Name* | *Default*                  | *Description*                                                |
|--------|----------------------------|--------------------------------------------------------------|
| `cmd`    | Mandatory `text-note` or `subscribe` or `filter` | Select the action to, `text-note` or `subscribe`             |
| `relay` | Mandatory                  | Relay address                                                |
| `pk` | Generate a new private key | Private key used to sign the event, should be in nsec format |
| `nym-client` | `ws://127.0.0.1:1977`      | nym-client to use on the client                              |

#### Subscribe to events

| *Name* | *Default*                  | *Description*                                                |
|--------|----------------------------|--------------------------------------------------------------|
| `limit` | `100` | Number of filter to filter                                   |


```bash
python main.py --cmd subscribe --relay 2gc9QidpXs4YGKmphinsDhWTHxdy2TZgWYWz2VenN5jL.dkwwJqS1zXa9BuPAFdniRN2HxFvAbTybAmrUHGAT5KV@2BuMSfMW3zpeAjKXyKLhmY4QW1DXurrtSPEJ6CjX3SEh 
```

#### Post new text note


| *Name* | *Default*                  | *Description*                                                |
|--------|----------------------------|--------------------------------------------------------------|
| `message`  | `This is a note published trough Nym mixnet, visit https://nymtech.net for more information` | Message to send on the note |


```bash
python main.py --cmd text-note --message "Hello world (from the Nym mixnet)" --relay 2gc9QidpXs4YGKmphinsDhWTHxdy2TZgWYWz2VenN5jL.dkwwJqS1zXa9BuPAFdniRN2HxFvAbTybAmrUHGAT5KV@2BuMSfMW3zpeAjKXyKLhmY4QW1DXurrtSPEJ6CjX3SEh 
```


#### Filter events

| *Name* | *Default*                  | *Description*                                                |
|--------|----------------------------|--------------------------------------------------------------|
| `kind`  | `1` | Event kind to filter, separate by `,` |
| `author` | `npub1nftkhktqglvcsj5n4wetkpzxpy4e5x78wwj9y9p70ar9u5u8wh6qsxmzqs` | Public key posted event to filter, npub format, separate by `,` |
| `since` | `None` | Since event to filter, epoch format |

```bash
python main.py --cmd filter --author npub1nftkhktqglvcsj5n4wetkpzxpy4e5x78wwj9y9p70ar9u5u8wh6qsxmzqs --relay 2gc9QidpXs4YGKmphinsDhWTHxdy2TZgWYWz2VenN5jL.dkwwJqS1zXa9BuPAFdniRN2HxFvAbTybAmrUHGAT5KV@2BuMSfMW3zpeAjKXyKLhmY4QW1DXurrtSPEJ6CjX3SEh 
```
