
# Nostr-Nym


## Not trough Nym

To use Nostr with CLI, [nostr-tool](https://github.com/0xtrr/nostr-tool) is good

## Create an event

```
nostr-tool -r <relay URI> text-note -c "Hello world (from the mixnet)"
```

### Trough Nym 

## Subscribe to event

```
echo '{"type": "sendAnonymous", "message": "[\"REQ\", \"RAND\", {\"limit\": 2}]", "recipient": "<service provider nym-client id>", "replySurbs": 100}' | websocat <nym-client URI>
```
