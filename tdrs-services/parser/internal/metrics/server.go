package metrics

import (
	"context"
	"log/slog"
	"time"

	"go-parser/internal/logging"
)

// ServerConfig controls metrics server lifecycle management.
type ServerConfig struct {
	Enabled       bool
	ServerMode    string
	ListenAddress string
	Path          string
}

type MetricsServer struct {
	enabled       bool
	serverMode    string
	listenAddress string
	path          string
	server        *MetricServer
}

// NewMetricsServer creates a manager for the configured metrics endpoint.
func NewMetricsServer(cfg ServerConfig) *MetricsServer {
	return &MetricsServer{
		enabled:       cfg.Enabled,
		serverMode:    cfg.ServerMode,
		listenAddress: cfg.ListenAddress,
		path:          cfg.Path,
	}
}

// Start starts the metrics endpoint when enabled.
func (s *MetricsServer) Start(ctx context.Context) error {
	if !s.enabled {
		return nil
	}

	server, err := StartMetricServer(ctx, MetricServerConfig{
		ServerMode:    s.serverMode,
		ListenAddress: s.listenAddress,
		Path:          s.path,
	})
	if err != nil {
		return err
	}
	s.server = server

	logging.Info(ctx, "metrics server started",
		slog.String(logging.KeyStage, "metrics"),
		slog.String("listen_address", server.Address()),
		slog.String("path", s.path),
	)
	return nil
}

// Shutdown stops the metrics endpoint when it was started.
func (s *MetricsServer) Shutdown() {
	if s.server == nil {
		return
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := s.server.Shutdown(shutdownCtx); err != nil {
		logging.Error(context.Background(), "metrics server shutdown failed",
			slog.String(logging.KeyStage, "metrics"),
			slog.Any(logging.KeyError, err),
		)
	}
}
