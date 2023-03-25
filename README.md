
# Nostr-Nym

[![asciicast](https://asciinema.org/a/569963.svg)](https://asciinema.org/a/569963)

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

### Publish event

Use [nostrtool](https://nostrtool.com/) to generate a raw event

Format

{"type": "sendAnonymous","message": "[\"EVENT\",<raw event>]","replySurbs": 100}


Example

```json
{"type": "sendAnonymous","message": "[\"EVENT\", {   \"id\": \"5b67177796c9b85284f3c56ff33823eb1bf9357513c4d903ff2ee52f0f08da4d\",   \"pubkey\": \"eddcc284db2f1a1f2a432fbfceb46f50715b6c10741a89b6ae8a0cda3eff230c\",   \"created_at\": 1679687002,   \"kind\": 1,   \"tags\": [],   \"content\": \"TESTING the notifying message\",   \"sig\": \"2f1bc7458c0da0659d6b9d9bd7d61439d11a7195ed9780f32a03e9ecb088e755a79415bb456fe33a499f4df310b8bca5e0082d778b8ab759e4a2df9a66fe8b45\" }]", "recipient": "7W6fQsAT6sdsqFxwUJBRZFEJkSLncQzTzvN4rmXnc2vi.29MhA8hD1dsxLqEbqi6xXSEkhc1bARnUApxvwn8tfauB@E7BuKRJw4XD8pYmLHEfZ94waoZsyuJupYRQrBiC5FQLB","replySurbs": 100}
```


{"type": "sendAnonymous","message": "[\"REQ\", \"RAND\", {\"limit\": 2}]","recipient": "9fa8LFUxg48oHDZZdQhUiKoifQhDGP6CCVcgKQTXWTWT.8c3aQjfbRLSqvczE3RwzBUjwsnWbQQ49nH8n8ePMdKLF@7fiZtNL1RACQTwGrKLBT9nbY77bfwZnX9rqcWqc53qgv", "replySurbs": 100}
