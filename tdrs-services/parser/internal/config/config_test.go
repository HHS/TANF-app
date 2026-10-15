package config

import (
	"testing"
	"time"
)

func TestDefaultConfig_NonZeroValues(t *testing.T) {
	cfg := DefaultConfig()

	checks := []struct {
		name string
		ok   bool
	}{
		{"Global.LogLevel", cfg.Global.LogLevel != ""},
		{"Global.ConfigDir", cfg.Global.ConfigDir != ""},
		{"SchemaFiles", len(cfg.SchemaFiles) > 0},
		{"FilespecFiles", len(cfg.FilespecFiles) > 0},
		{"Metrics.Enabled", cfg.Metrics.Enabled},
		{"Metrics.ListenAddress", cfg.Metrics.ListenAddress != ""},
		{"Metrics.Path", cfg.Metrics.Path != ""},
		{"Server.Mode", cfg.Server.Mode != ""},
		{"Server.Celery.Queue", cfg.Server.Celery.Queue != ""},
		{"Pipeline.NumWorkers", cfg.Pipeline.NumWorkers > 0},
		{"Pipeline.WorkBufferSize", cfg.Pipeline.WorkBufferSize > 0},
		{"Pipeline.PoolPrewarmSize", cfg.Pipeline.PoolPrewarmSize > 0},
		{"Writer.FlushThreshold", cfg.Writer.FlushThreshold > 0},
		{"Writer.ErrorFlushThreshold", cfg.Writer.ErrorFlushThreshold > 0},
		{"Validation.ShortCircuit", cfg.Validation.ShortCircuit},
		{"Validation.ValidatorFiles", len(cfg.Validation.ValidatorFiles) > 0},
		{"Database.MaxConns", cfg.Database.MaxConns > 0},
		{"Database.TablePrefix", cfg.Database.TablePrefix != ""},
		{"Database.MinConns", cfg.Database.MinConns > 0},
		{"Database.MaxConnLifetime", cfg.Database.MaxConnLifetime > 0},
		{"Database.MaxConnIdleTime", cfg.Database.MaxConnIdleTime > 0},
		{"Database.HealthCheckPeriod", cfg.Database.HealthCheckPeriod > 0},
		{"Storage.Source", cfg.Storage.Source != ""},
	}

	for _, c := range checks {
		if !c.ok {
			t.Errorf("DefaultConfig().%s has zero/empty value", c.name)
		}
	}
}

func TestTestConfig_ConservativeValues(t *testing.T) {
	def := DefaultConfig()
	test := TestConfig()

	if test.Pipeline.NumWorkers >= def.Pipeline.NumWorkers {
		t.Errorf("TestConfig workers (%d) should be less than default (%d)",
			test.Pipeline.NumWorkers, def.Pipeline.NumWorkers)
	}
	if test.Pipeline.WorkBufferSize >= def.Pipeline.WorkBufferSize {
		t.Errorf("TestConfig buffer (%d) should be less than default (%d)",
			test.Pipeline.WorkBufferSize, def.Pipeline.WorkBufferSize)
	}
	if test.Database.URL == "" {
		t.Error("TestConfig should have a non-empty database URL")
	}
}

func TestDefaultConfig_PreservesExistingDefaults(t *testing.T) {
	cfg := DefaultConfig()

	// Verify defaults match expected production values
	if cfg.Pipeline.NumWorkers != 16 {
		t.Errorf("NumWorkers = %d, want 16", cfg.Pipeline.NumWorkers)
	}
	if cfg.Database.MaxConnLifetime != 30*time.Minute {
		t.Errorf("MaxConnLifetime = %v, want 30m", cfg.Database.MaxConnLifetime)
	}
	if cfg.Database.HealthCheckPeriod != 30*time.Second {
		t.Errorf("HealthCheckPeriod = %v, want 30s", cfg.Database.HealthCheckPeriod)
	}
	if cfg.Database.TablePrefix != DefaultTablePrefix {
		t.Errorf("TablePrefix = %q, want %q", cfg.Database.TablePrefix, DefaultTablePrefix)
	}
	if cfg.Server.Celery.Queue != "go-parser" {
		t.Errorf("QueueName = %q, want go-parser", cfg.Server.Celery.Queue)
	}
	if !cfg.Metrics.Enabled {
		t.Error("Metrics.Enabled = false, want true")
	}
	if cfg.Metrics.ListenAddress != ":9809" {
		t.Errorf("Metrics.ListenAddress = %q, want :9809", cfg.Metrics.ListenAddress)
	}
	if cfg.Metrics.Path != "/metrics" {
		t.Errorf("Metrics.Path = %q, want /metrics", cfg.Metrics.Path)
	}
}
