
# Nostr-Nym Proxy

Nostr-nym is a proxy for using Nostr through the Nym Mixnet. It stands between Nostr users and a specific Nostr relay, preferrably on the same machine as the relay, allowing users to connect to this relay without leaking their IP address to it.

## How to run this?

### Parameters

These can be provided by arguments or environement variable. Environment variables have precedence over arguments passed by CLI.

| CLI short | CLI long | Env variable | Default value | Description |
|:-----:|:-----:|:-----:|:-----:|-----|
| `-l` | `--log-level` | `LOG_LEVEL` | `info` | Log level |
| `-c` | `--nym-client-ws` | `NYM_CLIENT_WS` | `127.0.0.1:1977` | Address of the nym-client to listen to |
| `-r` | `--nostr-relay-ws` | `NOSTR_RELAY_WS` | `127.0.0.1:1700` | Address of the nostr relay to forward messages to |
| `-d` | `--nym-client-log-level` | `NYM_CLIENT_LOG_LEVEL` | `""` | Log level of socket connection to Nym mixnet |
| `-s` | `--nostr-relay-log-level` | `NOSTR_RELAY_LOG_LEVEL` | `""` | Log level of socket connection to Nostr relay |

The log level values that can be used are: `trace`, `debug`, `info`, `warn`, `error` (`fatal` and `panic` are not used). Leave blank to disable logging.

Hereafter are presented several ways to run this software, depending on your need.

Note that in any case, a running nym-client and Nostr relay are required. You need to have both ready. The docker-compose option include both nym-client and Nostr relay. 

### Code

```bash
# Clone this repository
git clone https://github.com/notrustverify/nostr-nym

# Move inside the freshly downloaded folder
cd nostr-nym

# Run the software
go run .
```
You can provide parameters as explained above.

### Docker
The most straightforward
```bash
# Download and run our image. Parameters are provided via env variable (using -e in docker invocation)
docker run --name nostr-nym -e LOG_LEVEL=info notrustverify/nostr-nym
```

You can see the Client ID of the proxy in the logs.

If you want to include our image in your docker-compose, check our docker-compose.yml file!

### Docker Compose

This option will run an instance of the nym-client and a nostr relay, for convenience, in addition to a docker image of this code (fetched from Docker Hub). If you want to build yours locally, instead of using our image, add `-f docker-compose.build.yml` to the `docker compose` commands below to use the _docker-compose.build.yml_ file instead.

```bash
# Clone this repository
git clone https://github.com/notrustverify/nostr-nym

# Move inside the freshly downloaded folder
cd nostr-nym
cp example.docker-compose.yml docker-compose.yml

# Set the correct rights for docker containers to be allowed to access their volumes
mkdir ./nym-client-data
sudo chown -R 10000:10000 ./nym-client-data

# Build and start containers
docker compose up -d

# The containers can be stopped using, from the same folder
docker compose down
```

You can see the Client ID of the proxy in the logs.

Note: In the logs, you may notice that a first instance of this software fails to connect to the nym-client. It is due to the fact that the nym-client is not ready yet and so the proxy, which fails, will restart and then connect. Nothing to worry here.

## Contribute

If you want to edit this piece of code, we prepared a special docker-compose for you, so that you can work on the code and have the required services running around. We suggest you follow these instructions.

```bash
# Clone this repository
git clone https://github.com/notrustverify/nostr-nym

# Move inside the freshly downloaded folder
cd nostr-nym

# Set the correct rights for the nym-client to be allowed to access their volume
sudo chmod -R 10000:10000 ./nym-client-data

# Start the docker-compose for development
docker-compose -f docker-compose.dev.yaml up -d

# You can run the proxy with the following parameters (passed by CLI for example)
go run . --nym-client-ws 127.0.0.1:10977 --nostr-relay-ws 127.0.0.1:7000 --log-level debug

# Or you can use our Makefile for this
make run-debug

# When you want to stop the services stop the docker compose by using, from the same folder
docker-compose -f docker-compose.dev.yaml down
```

## License

This code is released under the GPLv3+ license.
