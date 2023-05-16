package main

import (
	"os"
	"strings"
	"time"

	"github.com/rs/zerolog"
)

/******************************************************************
 * Logger stuff
 ******************************************************************/

const ComponentField = "component"
const IdField = "identifier"

var PARTS_ORDER = []string{
	zerolog.TimestampFieldName,
	zerolog.LevelFieldName,
	zerolog.CallerFieldName,
	zerolog.MessageFieldName,
}

func EnsureLogLevelIsValidElseDefault(logLevel string, defaultValue string) string {
	level, e := zerolog.ParseLevel(logLevel)
	if nil != e {
		return defaultValue
	}
	return level.String()
}

func GetLoggerLevel(logLevel string) zerolog.Level {
	lvl := strings.ToLower(logLevel)

	level, e := zerolog.ParseLevel(lvl)
	if nil != e {
		level = zerolog.Disabled
	}

	return level
}

func GetLogger(logLevel string) zerolog.Logger {

	level := GetLoggerLevel(logLevel)

	logger := zerolog.New(zerolog.ConsoleWriter{
		Out:        os.Stdout,
		TimeFormat: time.RFC3339,
		PartsOrder: PARTS_ORDER,
	})

	return logger.Level(level).
		With().Timestamp().Logger().
		With().Caller().Logger()
}
