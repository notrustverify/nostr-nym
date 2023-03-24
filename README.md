
# Nostr-Nym


## Not trough Nym

To use Nostr with CLI, [nostr-tool](https://github.com/0xtrr/nostr-tool) is good

### Create an event

```
nostr-tool -r <relay URI> text-note -c "Hello world (from the mixnet)"
```

## Trough Nym

To use Nym, download [nym-client](https://github.com/nymtech/nym/releases)

### Use nym-client

1. init `nym-client init --id nostr-relay`
1. run `nym-client run --id nostr-relay`

### Subscribe to event

```json
{"type": "sendAnonymous","message": "[\"REQ\", \"RAND\", {\"limit\": 2}]","recipient": "7W6fQsAT6sdsqFxwUJBRZFEJkSLncQzTzvN4rmXnc2vi.29MhA8hD1dsxLqEbqi6xXSEkhc1bARnUApxvwn8tfauB@E7BuKRJw4XD8pYmLHEfZ94waoZsyuJupYRQrBiC5FQLB", "replySurbs": 100}
```

For example
```
echo '{"type": "sendAnonymous", "message": "[\"REQ\", \"RAND\", {\"limit\": 2}]", "recipient": "<service provider nym-client id>", "replySurbs": 100}' | websocat <nym-client URI>
```

### Search
```json
{"type": "sendAnonymous","message": "[\"REQ\", \"\", {\"search\": \"hello\"}]","recipient": "7W6fQsAT6sdsqFxwUJBRZFEJkSLncQzTzvN4rmXnc2vi.29MhA8hD1dsxLqEbqi6xXSEkhc1bARnUApxvwn8tfauB@E7BuKRJw4XD8pYmLHEfZ94waoZsyuJupYRQrBiC5FQLB", "replySurbs": 100}
```

