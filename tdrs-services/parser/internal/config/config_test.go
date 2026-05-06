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
		{"Server.Celery.Queue", cfg.Server.Celery.Queue != ""},
		{"Pipeline.NumWorkers", cfg.Pipeline.NumWorkers > 0},
		{"Pipeline.WorkBufferSize", cfg.Pipeline.WorkBufferSize > 0},
		{"Pipeline.PoolPrewarmSize", cfg.Pipeline.PoolPrewarmSize > 0},
		{"Writer.FlushThreshold", cfg.Writer.FlushThreshold > 0},
		{"Writer.ErrorFlushThreshold", cfg.Writer.ErrorFlushThreshold > 0},
		{"Validation.ShortCircuit", cfg.Validation.ShortCircuit},
		{"Validation.ValidatorFiles", len(cfg.Validation.ValidatorFiles) > 0},
		{"Database.MaxConns", cfg.Database.MaxConns > 0},
		{"Database.ShadowMode", cfg.Database.ShadowMode},
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
	if got := cfg.Database.EffectiveTablePrefix(); got != DefaultTablePrefix {
		t.Errorf("EffectiveTablePrefix = %q, want %q", got, DefaultTablePrefix)
	}
	if cfg.Server.Celery.Queue != "go-parser" {
		t.Errorf("QueueName = %q, want go-parser", cfg.Server.Celery.Queue)
	}
}

func TestDatabaseConfig_EffectiveTablePrefix(t *testing.T) {
	tests := []struct {
		name string
		cfg  DatabaseConfig
		want string
	}{
		{
			name: "shadow mode uses configured prefix",
			cfg:  DatabaseConfig{ShadowMode: true, TablePrefix: "shadow_"},
			want: "shadow_",
		},
		{
			name: "production mode disables prefix",
			cfg:  DatabaseConfig{ShadowMode: false, TablePrefix: "shadow_"},
			want: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.cfg.EffectiveTablePrefix(); got != tt.want {
				t.Errorf("EffectiveTablePrefix() = %q, want %q", got, tt.want)
			}
		})
	}
}
