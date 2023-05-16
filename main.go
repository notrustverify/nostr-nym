package main

import (
	"fmt"
	"os"
	"os/signal"
	"regexp"
	"strings"

	NymSocketManager "github.com/notrustverify/nymsocketmanager"
	pflag "github.com/spf13/pflag"
)

var WS_PREFIX = regexp.MustCompile(`^wss?://`)

var NYM_CLIENT_WS = pflag.StringP("nym-client-ws", "c", "127.0.0.1:1977", "The ws:// address of the nym-client to listen to.")
var NOSTR_RELAY_WS = pflag.StringP("nostr-relay-ws", "r", "127.0.0.1:1700", "The ws:// address of the nostr relay to forward messages to.")

// Change the default value of the flag for changing the default logging level
const DEFAULT_LOG_LEVEL = "info"

var LOG_LEVEL = pflag.StringP("log-level", "l", DEFAULT_LOG_LEVEL, "Log level (trace, debug, info, warn, error). Leave empty to hide logs.")
var NYM_CLIENT_LOG_LEVEL = pflag.StringP("nym-client-log-level", "d", "", "Log level for the NymSocketManager (trace, debug, info, warn, error). Leave empty to hide logs.")
var NOSTR_RELAY_LOG_LEVEL = pflag.StringP("nostr-relay-log-level", "s", "", "Log level for the SocketManager connected to the Nostr relay (trace, debug, info, warn, error). Leave empty to hide logs.")

func main() {
	// Handling of arguments:
	// 1. Command line args are parsed, default values are set
	pflag.Parse()

	// 2. For each of them, find if equivalent env variable is defined
	// (flag is capitalized and '-' are replaced by '_', so "a-b_c" maps to "A_B_C")
	pflag.VisitAll(func(f *pflag.Flag) {
		capitalizedName := strings.ToUpper(f.Name)
		transformedName := strings.ReplaceAll(capitalizedName, "-", "_")
		val, ok := os.LookupEnv(transformedName)
		if ok {
			pflag.Set(f.Name, val)
		}
	})

	// Ensure WS addresses start with ws:// or wss:// (set to ws:// if not)
	pflag.VisitAll(func(f *pflag.Flag) {
		if f.Name[len(f.Name)-3:] == "-ws" && !WS_PREFIX.Match([]byte(f.Value.String())) {
			f.Value.Set(fmt.Sprintf("ws://%s", f.Value.String()))
		}
	})

	// Handle the shutdown of the signal
	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt)

	// Get logger
	loggerLevel := EnsureLogLevelIsValidElseDefault(*LOG_LEVEL, DEFAULT_LOG_LEVEL)
	logger := GetLogger(loggerLevel)
	logger.Info().Msg("Starting the NostrNym Proxy")

	// Instantiate list of actors
	listOfActors, e := NewListOfActors(&logger)
	if nil != e {
		logger.Error().Msgf("failed to create list of actors: %v", e)
		return
	}

	// Create NymSocketManager
	childLogger := logger.Level(GetLoggerLevel(*NYM_CLIENT_LOG_LEVEL))
	nymSocketManager, e := NymSocketManager.NewNymSocketManager(*NYM_CLIENT_WS, listOfActors.HandleMsgFromMixnet, &childLogger)
	if nil != e {
		logger.Error().Msgf("failed to create the NymSocketManager: %v", e)
		return
	}

	// Provide list of actors the function to send messages to the mixnet
	listOfActors.SetSendToMixnet(nymSocketManager.Send)

	// Start the NymSocketManager and collect ClientID
	stoppedSocketManager, e := nymSocketManager.Start()
	if nil != e {
		logger.Error().Msgf("failed to start the NymSocketManager: %v", e)
		return
	}

	fmt.Printf("Client id of this proxy is: %s\n", nymSocketManager.GetNymClientId())

	select {
	case <-stoppedSocketManager:
		stoppedSocketManager = nil
		logger.Debug().Msg("NymSocketManager has stopped (underlying connection closed)")

	case <-interrupt:
		logger.Debug().Msg("Received shutdown signal, closing...")
		nymSocketManager.Stop()
	}

	// We stop each actor
	listOfActors.StopAll()

	logger.Info().Msg("Leaving you now, enjoy your life!")
}
