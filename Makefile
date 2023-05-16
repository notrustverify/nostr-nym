
run:
	@go run .

run-debug:
	@LOG_LEVEL=debug NOSTR_RELAY_WS=127.0.0.1:7000 NYM_CLIENT_WS=127.0.0.1:10977 go run .

lint:s
	@# Coding style static check.
	@go get -v honnef.co/go/tools/cmd/staticcheck
	@go mod tidy
	staticcheck ./...

vet:
	go vet ./...
