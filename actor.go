package main

import (
	"sync"

	NymSocketManager "github.com/notrustverify/nymsocketmanager"
	"github.com/rs/zerolog"
	"golang.org/x/xerrors"
)

func NewActor(senderTag string, sendToMixnet func(NymSocketManager.NymMessage) error, askForRemoval func(), parentLogger *zerolog.Logger) (*Actor, error) {

	if len(senderTag) == 0 {
		err := xerrors.Errorf("senderTag needs to be non-empty")
		return nil, err
	}

	if nil == sendToMixnet {
		err := xerrors.Errorf("function to sendToMixnet needs to be defined")
		return nil, err
	}

	if nil == askForRemoval {
		err := xerrors.Errorf("function to askForDeletion needs to be defined")
		return nil, err
	}

	if nil == parentLogger {
		err := xerrors.Errorf("logger needs to be defined")
		return nil, err
	}

	actorLogger := parentLogger.With().Str(ComponentField, "actor").Str(IdField, senderTag).Logger()

	return &Actor{
		senderTag:     senderTag,
		socketManager: nil,
		sendToMixnet:  sendToMixnet,
		askForRemoval: askForRemoval,
		logger:        &actorLogger,
	}, nil
}

type Actor struct {
	sync.Mutex

	// Identifier in the mixnet
	senderTag string

	selfInstanceStoppedChan chan bool

	// Socket to connect to relay
	socketManager *NymSocketManager.SocketManager

	// Function to reply to the mixnet
	sendToMixnet func(NymSocketManager.NymMessage) error

	// Function to ask to be removed from the list
	askForRemoval func()

	logger *zerolog.Logger
}

// An actor is running if they have a defined socketManager which is connected to the relay
func (a *Actor) IsRunning() bool {
	a.Lock()
	defer a.Unlock()
	return nil != a.socketManager && a.socketManager.IsRunning()
}

func (a *Actor) Start() (chan bool, error) {
	a.Lock()
	defer a.Unlock()

	a.logger.Debug().Msgf("starting actor %v", a.senderTag)

	// Ensure not already started
	if nil != a.socketManager && !a.socketManager.IsRunning() {
		a.logger.Warn().Msg("actor already created and running. Resuming...")
		return nil, nil
	}

	// Create and start socketManager for this actor
	var e error
	childLogger := a.logger.Level(GetLoggerLevel(*NOSTR_RELAY_LOG_LEVEL))
	a.socketManager, e = NymSocketManager.NewSocketManager(*NOSTR_RELAY_WS, func(msg []byte, _ func([]byte) error) {
		a.ForwardNostrMessageToNym(msg)
	}, &childLogger)
	if nil != e {
		err := xerrors.Errorf("failed to create socketManager: %v", e)
		a.logger.Err(err).Msg("")
		return nil, err
	}

	_, e = a.socketManager.Start()
	if nil != e {
		err := xerrors.Errorf("failed to start socketManager: %v", e)
		a.logger.Err(err).Msg("")
		a.selfDestruct()
		return nil, err
	}

	a.selfInstanceStoppedChan = make(chan bool, 1)

	a.logger.Debug().Msgf("started actor %v", a.senderTag)

	return a.selfInstanceStoppedChan, nil
}

func (a *Actor) Stop() {
	a.Lock()
	defer a.Unlock()

	a.logger.Info().Msgf("stopping actor %v", a.senderTag)

	// Ensure not already stopped
	if nil == a.socketManager {
		a.logger.Warn().Msg("actor already stopped. Resuming...")
		return
	}

	a.selfDestruct()

	a.logger.Info().Msgf("stopped actor %v", a.senderTag)
}

// selfDestruct is called by method that already acquired the lock
func (a *Actor) selfDestruct() {
	a.logger.Debug().Msg("selfDestructing")

	// If already stopped, ignore
	if nil == a.socketManager {
		return
	}

	defer close(a.selfInstanceStoppedChan)

	if a.socketManager.IsRunning() {
		a.logger.Debug().Msgf("actor %v is still running. Stopping...", a.senderTag)
		a.socketManager.Stop()
	}
	a.socketManager = nil

	a.logger.Debug().Msg("selfDestructed")
}

func (a *Actor) ForwardNymMessageToNostr(msg NymSocketManager.NymReceived) {
	a.Lock()
	defer a.Unlock()

	// Get Nostr message embedded in Nym message
	nostrMessage := msg.Message

	// Handle custom "quit" message to remove actor
	if nostrMessage == "quit" {
		a.logger.Info().Msgf("received \"quit\" message...")
		a.selfDestruct()
		a.askForRemoval()
		return
	}

	a.logger.Info().Msgf("forwarding message to Nostr:\"%v\"", nostrMessage)

	// Ensure connection is alive
	if nil == a.socketManager || !a.socketManager.IsRunning() {
		a.logger.Warn().Msg("actor is stopped. Ignoring...")
		return
	}

	// Forward message to Nostr
	a.socketManager.Send([]byte(nostrMessage))
}

// ForwardNostrMessageToNym handles incoming message from the Nostr relay and forward them to the Nym mixnet
// Not locking the Actor since no existential modification is made to it. Upstream sending function might be locked.
func (a *Actor) ForwardNostrMessageToNym(msg []byte) {

	// Embed Nostr message into NymReplyMessage
	nymMessage := NymSocketManager.NewNymReply(a.senderTag, string(msg)).(NymSocketManager.NymReply)

	a.logger.Info().Msgf("forwarding message to Nym:\"%v\"", nymMessage.Message)

	e := a.sendToMixnet(nymMessage)
	if nil != e {
		a.logger.Warn().Msgf("failed to forward message to mixnet: %v", e)
		return
	}
}
