# syntax=docker/dockerfile:1

# Dockerfile according https://docs.docker.com/language/golang/build-images/

FROM golang:1.20 AS build-stage

# Set destination for COPY
WORKDIR /app

# Download Go modules
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code. Note the slash at the end, as explained in
# https://docs.docker.com/engine/reference/builder/#copy
COPY *.go ./

# Build
RUN CGO_ENABLED=0 GOOS=linux go build -o /nostr-nym-proxy

# Run the tests in the container
#FROM build-stage AS run-test-stage
#RUN go test -v ./...

# Deploy the application binary into a lean image
FROM gcr.io/distroless/base-debian11 AS build-release-stage

WORKDIR /

COPY --from=build-stage /nostr-nym-proxy /nostr-nym-proxy

USER nonroot:nonroot

# Run
CMD ["/nostr-nym-proxy"]
