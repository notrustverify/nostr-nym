package main

import (
	"sync"

	NymSocketManager "github.com/notrustverify/nymsocketmanager"
	"github.com/rs/zerolog"
	"golang.org/x/xerrors"
)

func NewListOfActors(parentLogger *zerolog.Logger) (*listOfActors, error) {
	if nil == parentLogger {
		err := xerrors.Errorf("logger needs to be defined")
		return nil, err
	}

	listOfActorsLogger := parentLogger.With().Str(ComponentField, "ListOfActors").Logger()

	listOfActorsLogger.Debug().Msg("Create new list of actors")

	return &listOfActors{
		actors: make(map[string]*Actor),
		logger: &listOfActorsLogger,
	}, nil
}

type listOfActors struct {
	sync.Mutex

	actors map[string]*Actor

	sendToMixnet func(NymSocketManager.NymMessage) error

	logger *zerolog.Logger
}

// We can ignore the second parameter here, as the function to send a message to the mixnet is
// already provided to the list of actors.
func (l *listOfActors) HandleMsgFromMixnet(msg NymSocketManager.NymReceived, _ func(NymSocketManager.NymMessage) error) {

	if len(msg.SenderTag) == 0 {
		l.logger.Warn().Msgf("no senderTag in received message: %v. Ignoring...", msg)
		return
	}

	l.logger.Info().Msgf("Got message from %s: %s", msg.SenderTag, msg.Message)

	// Retrieve corresponding actor
	actor, e := l.GetActorWithId(msg.SenderTag)
	if nil != e {
		l.logger.Warn().Msgf("failed to get actor %v: %v. Ignoring message from mixnet", msg.SenderTag, e)
		return
	}

	actor.ForwardNymMessageToNostr(msg)
}

func (l *listOfActors) SetSendToMixnet(_sendToMixnet func(NymSocketManager.NymMessage) error) error {
	l.Lock()
	defer l.Unlock()

	if nil == _sendToMixnet {
		err := xerrors.Errorf("the function to send messages to the mixnet cannot be undefined")
		l.logger.Err(err).Msg("")
		return err
	}

	l.sendToMixnet = _sendToMixnet
	return nil
}

func (l *listOfActors) GetNbrActors() int {
	l.Lock()
	defer l.Unlock()
	return len(l.actors)
}

// As this function create and start actors, the sendToMixnet function should be previously defined
func (l *listOfActors) GetActorWithId(id string) (*Actor, error) {
	l.Lock()
	defer l.Unlock()

	l.logger.Debug().Msgf("getting actor with id: %v (actor count: %d)", id, len(l.actors))

	actor, ok := l.actors[id]

	// If actor does not exist, we create one
	if !ok {
		l.logger.Debug().Msgf("actor %v does not exist yet. Creating...", id)

		var e error
		actor, e = NewActor(id, l.sendToMixnet, func() { l.removeActor(id) }, l.logger)
		if nil != e {
			err := xerrors.Errorf("failed to create new actor with senderTag %v: %v", id, e)
			l.logger.Err(err).Msg("")
			return nil, err
		}

		// Add it to the list
		l.actors[id] = actor
	}

	// Ensure actor is started (new actors need to be started)
	if !actor.IsRunning() {

		l.logger.Debug().Msgf("actor %v is not running. Starting....", id)

		_, e := actor.Start()
		if nil != e {
			err := xerrors.Errorf("failed to start actor with id %v: %v", actor.senderTag, e)
			l.logger.Err(err).Msg("")
			return nil, err
		}
	}

	l.logger.Debug().Msgf("found actor with id: %v (actor count: %d)", id, len(l.actors))

	return actor, nil
}

// Gracefully stop all actors
func (l *listOfActors) StopAll() {
	l.Lock()
	defer l.Unlock()
	l.logger.Debug().Msgf("stopping all %d actors...", len(l.actors))

	// Could be done in parallel with go routines and timeout
	for _, a := range l.actors {
		a.Stop()
	}

	l.logger.Debug().Msg("stopped all actors...")
}

// removeActor is called by actors to remove themselves when their socket connection closes
func (l *listOfActors) removeActor(id string) {
	l.Lock()
	defer l.Unlock()

	l.logger.Debug().Msgf("removing actor with id %v (actor count: %d)", id, len(l.actors))

	_, ok := l.actors[id]
	if !ok {
		l.logger.Warn().Msgf("cannot remove actor with id %v: actor does not exists", id)
		return
	}

	// Since method is called by actors on after selfDestruction, no need to Stop them.

	delete(l.actors, id)
	l.logger.Debug().Msgf("removed actor with id %v (actor count %d)", id, len(l.actors))
}
