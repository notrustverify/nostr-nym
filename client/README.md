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

| *Name* | *Default*                  | *Description*                                               |
|--------|----------------------------|-------------------------------------------------------------|
| `cmd`    | Mandatory `text-note` or `subscribe`                 | Select the action to, `text-note` or `subscribe`            |
| `relay` | Mandatory                  | Relay address                                               |
| `pk` | Generate a new private key | Private key used to sign the event, should be in hex format |
| `message`  | `This is a note published trough Nym mixnet, visit https://nymtech.net for more information` | Message to send on the note |
| `nym-client` | `ws://127.0.0.1:1977`      | nym-client to use on the client |
| `limit` | `100` | Number of filter to filter |

#### Subscribe to events

```bash
python main.py --cmd subscribe --relay 2gc9QidpXs4YGKmphinsDhWTHxdy2TZgWYWz2VenN5jL.dkwwJqS1zXa9BuPAFdniRN2HxFvAbTybAmrUHGAT5KV@2BuMSfMW3zpeAjKXyKLhmY4QW1DXurrtSPEJ6CjX3SEh 
```

#### Post new text note

```bash
python main.py --cmd text-note --message "Hello world (from the Nym mixnet)" --relay 2gc9QidpXs4YGKmphinsDhWTHxdy2TZgWYWz2VenN5jL.dkwwJqS1zXa9BuPAFdniRN2HxFvAbTybAmrUHGAT5KV@2BuMSfMW3zpeAjKXyKLhmY4QW1DXurrtSPEJ6CjX3SEh 
```


#### Search post

```bash
python main.py --cmd text-note --message "Hello world (from the Nym mixnet)" --relay 2gc9QidpXs4YGKmphinsDhWTHxdy2TZgWYWz2VenN5jL.dkwwJqS1zXa9BuPAFdniRN2HxFvAbTybAmrUHGAT5KV@2BuMSfMW3zpeAjKXyKLhmY4QW1DXurrtSPEJ6CjX3SEh 
```