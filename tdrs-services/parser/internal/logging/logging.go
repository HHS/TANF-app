package logging

import (
	"context"
	"fmt"
	"io"
	"log/slog"
	"os"
	"strings"
)

// Configure installs the process-wide structured logger.
func Configure(levelName string) error {
	level, err := ParseLevel(levelName)
	if err != nil {
		return err
	}
	ConfigureWriter(os.Stdout, level)
	return nil
}

// ConfigureWriter installs a JSON logger that writes to the provided writer.
func ConfigureWriter(w io.Writer, level slog.Level) {
	slog.SetDefault(slog.New(slog.NewJSONHandler(w, &slog.HandlerOptions{
		Level: level,
	})))
}

// Debug emits a debug log using slog.Attr fields. Avoid debug logs in parser hot paths.
func Debug(ctx context.Context, msg string, attrs ...slog.Attr) {
	slog.LogAttrs(ctx, slog.LevelDebug, msg, attrs...)
}

// Info emits an info log using slog.Attr fields.
func Info(ctx context.Context, msg string, attrs ...slog.Attr) {
	slog.LogAttrs(ctx, slog.LevelInfo, msg, attrs...)
}

// Warn emits a warning log using slog.Attr fields.
func Warn(ctx context.Context, msg string, attrs ...slog.Attr) {
	slog.LogAttrs(ctx, slog.LevelWarn, msg, attrs...)
}

// Error emits an error log using slog.Attr fields.
func Error(ctx context.Context, msg string, attrs ...slog.Attr) {
	slog.LogAttrs(ctx, slog.LevelError, msg, attrs...)
}

// Fatal emits an error log and exits with a non-zero status.
func Fatal(msg string, attrs ...slog.Attr) {
	slog.LogAttrs(context.Background(), slog.LevelError, msg, attrs...)
	os.Exit(1)
}

// ParseLevel converts config/CLI log-level values into slog levels.
func ParseLevel(levelName string) (slog.Level, error) {
	switch strings.ToLower(strings.TrimSpace(levelName)) {
	case "", "info":
		return slog.LevelInfo, nil
	case "debug":
		return slog.LevelDebug, nil
	case "warn", "warning":
		return slog.LevelWarn, nil
	case "error":
		return slog.LevelError, nil
	default:
		return slog.LevelInfo, fmt.Errorf("invalid log level %q: expected debug, info, warn, or error", levelName)
	}
}
