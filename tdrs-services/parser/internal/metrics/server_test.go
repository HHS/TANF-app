package metrics

import (
	"context"
	"io"
	"net/http"
	"strings"
	"testing"
)

func TestMetricsServerStartNoopsWhenDisabled(t *testing.T) {
	manager := NewMetricsServer(ServerConfig{Enabled: false})
	if err := manager.Start(context.Background()); err != nil {
		t.Fatalf("Start failed: %v", err)
	}
	manager.Shutdown()

	if manager.server != nil {
		t.Fatal("server = non-nil, want nil")
	}
}

func TestMetricsServerStartExposesConfiguredServerMode(t *testing.T) {
	manager := NewMetricsServer(ServerConfig{
		Enabled:       true,
		ServerMode:    "local",
		ListenAddress: "127.0.0.1:0",
		Path:          "/metrics",
	})
	if err := manager.Start(context.Background()); err != nil {
		t.Fatalf("Start failed: %v", err)
	}
	defer manager.Shutdown()

	RecordFileProcessed("TAN", 1, "success")

	resp, err := http.Get("http://" + manager.server.Address() + "/metrics")
	if err != nil {
		t.Fatalf("GET /metrics failed: %v", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("ReadAll failed: %v", err)
	}
	body := string(bodyBytes)
	want := `go_parser_files_processed_total{program="TAN",section="1",server_mode="local",status="success"} 1`
	if !strings.Contains(body, want) {
		t.Fatalf("metrics body missing %q\nbody:\n%s", want, body)
	}
}
