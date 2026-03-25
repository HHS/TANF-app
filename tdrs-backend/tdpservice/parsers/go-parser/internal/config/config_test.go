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
		{"Server.Mode", cfg.Server.Mode != ""},
		{"Pipeline.NumWorkers", cfg.Pipeline.NumWorkers > 0},
		{"Pipeline.WorkBufferSize", cfg.Pipeline.WorkBufferSize > 0},
		{"Pipeline.PoolPrewarmSize", cfg.Pipeline.PoolPrewarmSize > 0},
		{"Writer.FlushThreshold", cfg.Writer.FlushThreshold > 0},
		{"Writer.ErrorFlushThreshold", cfg.Writer.ErrorFlushThreshold > 0},
		{"Validation.ShortCircuit", cfg.Validation.ShortCircuit},
		{"Validation.ValidatorFiles", len(cfg.Validation.ValidatorFiles) > 0},
		{"Database.MaxConns", cfg.Database.MaxConns > 0},
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
}
