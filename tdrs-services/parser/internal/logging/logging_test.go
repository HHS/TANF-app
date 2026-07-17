package logging

import (
	"bytes"
	"context"
	"encoding/json"
	"log/slog"
	"testing"
)

func TestParseLevel(t *testing.T) {
	tests := []struct {
		name      string
		levelName string
		want      slog.Level
		wantErr   bool
	}{
		{name: "empty defaults to info", levelName: "", want: slog.LevelInfo},
		{name: "debug", levelName: "debug", want: slog.LevelDebug},
		{name: "info", levelName: "info", want: slog.LevelInfo},
		{name: "warn", levelName: "warn", want: slog.LevelWarn},
		{name: "warning", levelName: "warning", want: slog.LevelWarn},
		{name: "error", levelName: "error", want: slog.LevelError},
		{name: "invalid", levelName: "trace", wantErr: true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ParseLevel(tt.levelName)
			if tt.wantErr {
				if err == nil {
					t.Fatal("expected error")
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.want {
				t.Errorf("level = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestConfigureWriterEmitsJSON(t *testing.T) {
	var buf bytes.Buffer
	ConfigureWriter(&buf, slog.LevelDebug)

	Info(context.Background(), "parser event",
		slog.Int(KeyFileID, 42),
		slog.String(KeyStage, "test"),
	)

	var entry map[string]any
	if err := json.Unmarshal(buf.Bytes(), &entry); err != nil {
		t.Fatalf("log output is not JSON: %v", err)
	}
	if entry["msg"] != "parser event" {
		t.Errorf("msg = %v", entry["msg"])
	}
	if entry["level"] != "INFO" {
		t.Errorf("level = %v", entry["level"])
	}
	if entry["file_id"] != float64(42) {
		t.Errorf("file_id = %v", entry["file_id"])
	}
	if entry["stage"] != "test" {
		t.Errorf("stage = %v", entry["stage"])
	}
}

func TestEmitHelpersUseExpectedLevels(t *testing.T) {
	tests := []struct {
		name  string
		level string
		emit  func(context.Context, string, ...slog.Attr)
	}{
		{name: "debug", level: "DEBUG", emit: Debug},
		{name: "info", level: "INFO", emit: Info},
		{name: "warn", level: "WARN", emit: Warn},
		{name: "error", level: "ERROR", emit: Error},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var buf bytes.Buffer
			ConfigureWriter(&buf, slog.LevelDebug)

			tt.emit(context.Background(), "parser event", slog.Int(KeyFileID, 42))

			var entry map[string]any
			if err := json.Unmarshal(buf.Bytes(), &entry); err != nil {
				t.Fatalf("log output is not JSON: %v", err)
			}
			if entry["level"] != tt.level {
				t.Errorf("level = %v, want %s", entry["level"], tt.level)
			}
			if entry[KeyFileID] != float64(42) {
				t.Errorf("file_id = %v", entry[KeyFileID])
			}
		})
	}
}
