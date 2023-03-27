
# Nostr-Nym

Nostr-nym is a proxy to leverage the power of [Nym](https://nymtech.net) mixnet by giving the possibility to host a nostr  relay behind it in order to protect metadata connection (IP, data size) to be analyzed by ISP

A public relay is accessible with the following nym-client id:
`2gc9QidpXs4YGKmphinsDhWTHxdy2TZgWYWz2VenN5jL.dkwwJqS1zXa9BuPAFdniRN2HxFvAbTybAmrUHGAT5KV@2BuMSfMW3zpeAjKXyKLhmY4QW1DXurrtSPEJ6CjX3SEh`

A light nostr client is available under [client](client) folder to be able to interact with a nostr relay hosted on the mixnet

Demo
[![asciicast](https://asciinema.org/a/569964.svg)](https://asciinema.org/a/569964)


## Installation

#### Environment variables

##### nostr-nym

| Name                   | Default                | Description                                        |
|------------------------|------------------------|----------------------------------------------------|
| `NOSTR_RELAY_URI_PORT` | `ws://127.0.0.1:7000`| Nostr relay, format is `<ws>,<wss>://URL:PORT`     |
| `NYM_CLIENT_URI`       | `ws://nym-client:1977` | nym-client used to receive request from the mixnet |

##### nym-client

| Name                | Default     | Description                     |
|---------------------|-------------|---------------------------------|
| `NAME_CLIENT`       | `docker`    | Name to identify the nym-client |
| `LISTENING_ADDRESS` | `127.0.0.1` | Specify the listening interface |


### Using docker-compose

3 containers are included in it
 * nym-client: to receive or forward request in the mixnet
 * proxy: extract nostr event and open a websocket with the relay
 * relay: receive, store and forward event on Nostr

```bash

# copy example docker-compose file
cp example.docker-compose.yml docker-compose.yml

# change permissions for `nym-client` and `relay`

# start the containers
docker compose up -d

```

