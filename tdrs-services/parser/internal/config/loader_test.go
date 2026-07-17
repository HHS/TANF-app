package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadConfig_DefaultsOnly(t *testing.T) {
	// Point at a non-existent file — should return defaults
	cfg, err := LoadConfig("/tmp/nonexistent/parser.yaml")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	def := DefaultConfig()
	if cfg.Pipeline.NumWorkers != def.Pipeline.NumWorkers {
		t.Errorf("NumWorkers = %d, want default %d", cfg.Pipeline.NumWorkers, def.Pipeline.NumWorkers)
	}
	if cfg.Server.Mode != def.Server.Mode {
		t.Errorf("Server.Mode = %q, want default %q", cfg.Server.Mode, def.Server.Mode)
	}
}

func TestLoadConfig_ParsesParserYAML(t *testing.T) {
	dir := t.TempDir()
	content := `
global:
  log_level: debug
pipeline:
  num_workers: 42
  work_buffer_size: 512
server:
  mode: grpc
database:
  max_conns: 20
  shadow_mode: false
  table_prefix: "custom_"
`
	path := filepath.Join(dir, "parser.yaml")
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	cfg, err := LoadConfig(path)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if cfg.Pipeline.NumWorkers != 42 {
		t.Errorf("NumWorkers = %d, want 42", cfg.Pipeline.NumWorkers)
	}
	if cfg.Global.LogLevel != "debug" {
		t.Errorf("Global.LogLevel = %q, want debug", cfg.Global.LogLevel)
	}
	if cfg.Pipeline.WorkBufferSize != 512 {
		t.Errorf("WorkBufferSize = %d, want 512", cfg.Pipeline.WorkBufferSize)
	}
	if cfg.Server.Mode != "grpc" {
		t.Errorf("Server.Mode = %q, want grpc", cfg.Server.Mode)
	}
	if cfg.Database.MaxConns != 20 {
		t.Errorf("Database.MaxConns = %d, want 20", cfg.Database.MaxConns)
	}
	if cfg.Database.ShadowMode {
		t.Error("Database.ShadowMode = true, want false")
	}
	if cfg.Database.TablePrefix != "custom_" {
		t.Errorf("Database.TablePrefix = %q, want custom_", cfg.Database.TablePrefix)
	}
	if cfg.Database.EffectiveTablePrefix() != "" {
		t.Errorf("EffectiveTablePrefix = %q, want empty production prefix", cfg.Database.EffectiveTablePrefix())
	}
}

func TestLoadConfig_PartialYAML(t *testing.T) {
	dir := t.TempDir()
	// Only set pipeline block — everything else should retain defaults
	content := `
pipeline:
  num_workers: 8
`
	path := filepath.Join(dir, "parser.yaml")
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	cfg, err := LoadConfig(path)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if cfg.Pipeline.NumWorkers != 8 {
		t.Errorf("NumWorkers = %d, want 8", cfg.Pipeline.NumWorkers)
	}

	def := DefaultConfig()
	if cfg.Writer.FlushThreshold != def.Writer.FlushThreshold {
		t.Errorf("FlushThreshold = %d, want default %d", cfg.Writer.FlushThreshold, def.Writer.FlushThreshold)
	}
	if cfg.Database.MaxConns != def.Database.MaxConns {
		t.Errorf("MaxConns = %d, want default %d", cfg.Database.MaxConns, def.Database.MaxConns)
	}
}

func TestLoadConfig_EnvInterpolation(t *testing.T) {
	dir := t.TempDir()
	content := `
database:
  url: "${TEST_LOADER_DB_URL}"
`
	path := filepath.Join(dir, "parser.yaml")
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	os.Setenv("TEST_LOADER_DB_URL", "postgres://test:pass@localhost/testdb")
	defer os.Unsetenv("TEST_LOADER_DB_URL")

	cfg, err := LoadConfig(path)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	want := "postgres://test:pass@localhost/testdb"
	if cfg.Database.URL != want {
		t.Errorf("Database.URL = %q, want %q", cfg.Database.URL, want)
	}
}

func TestLoadConfig_InvalidYAML(t *testing.T) {
	dir := t.TempDir()
	content := `
pipeline:
  num_workers: [invalid yaml
`
	path := filepath.Join(dir, "parser.yaml")
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	_, err := LoadConfig(path)
	if err == nil {
		t.Error("expected error for invalid YAML, got nil")
	}
}
