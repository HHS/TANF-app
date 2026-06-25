package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCLI_DefaultConfigFile(t *testing.T) {
	cli, _, err := ParseCLI([]string{})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	// Kong type=path resolves to absolute, so just check it ends correctly
	if !filepath.IsAbs(cli.ConfigFile) {
		t.Errorf("ConfigFile should be absolute, got %q", cli.ConfigFile)
	}
	if filepath.Base(cli.ConfigFile) != "parser.yaml" {
		t.Errorf("ConfigFile should end with parser.yaml, got %q", cli.ConfigFile)
	}
}

func TestCLI_OverrideServerMode(t *testing.T) {
	cli, _, err := ParseCLI([]string{"--server.mode=grpc"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if cli.ServerMode != "grpc" {
		t.Errorf("ServerMode = %q, want grpc", cli.ServerMode)
	}
}

func TestCLI_OverrideDatabaseURL(t *testing.T) {
	cli, _, err := ParseCLI([]string{"--database.url=postgres://test:pass@localhost/db"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if cli.DatabaseURL != "postgres://test:pass@localhost/db" {
		t.Errorf("DatabaseURL = %q, want postgres://test:pass@localhost/db", cli.DatabaseURL)
	}
}

func TestCLI_OverrideGlobalLogLevel(t *testing.T) {
	cli, ctx, err := ParseCLI([]string{"--global.log-level=debug"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	cfg := DefaultConfig()
	cli.ApplyTo(cfg, ctx)

	if cfg.Global.LogLevel != "debug" {
		t.Errorf("Global.LogLevel = %q, want debug", cfg.Global.LogLevel)
	}
}

func TestCLI_OverrideGlobalLogLevelFromEnv(t *testing.T) {
	t.Setenv("GO_PARSER_LOG_LEVEL", "warn")

	cli, ctx, err := ParseCLI([]string{})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	cfg := DefaultConfig()
	cli.ApplyTo(cfg, ctx)

	if cfg.Global.LogLevel != "warn" {
		t.Errorf("Global.LogLevel = %q, want warn from GO_PARSER_LOG_LEVEL", cfg.Global.LogLevel)
	}
}

func TestCLI_OverrideDatabaseTablePrefix(t *testing.T) {
	cli, ctx, err := ParseCLI([]string{"--database.table-prefix=parser2_"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	cfg := DefaultConfig()
	cli.ApplyTo(cfg, ctx)

	if cfg.Database.TablePrefix != "parser2_" {
		t.Errorf("Database.TablePrefix = %q, want parser2_", cfg.Database.TablePrefix)
	}
}

func TestCLI_OverrideDatabaseShadowMode(t *testing.T) {
	cli, ctx, err := ParseCLI([]string{"--database.shadow-mode=false"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	cfg := DefaultConfig()
	cli.ApplyTo(cfg, ctx)

	if cfg.Database.ShadowMode {
		t.Error("Database.ShadowMode = true, want false")
	}
	if got := cfg.Database.EffectiveTablePrefix(); got != "" {
		t.Errorf("EffectiveTablePrefix = %q, want empty production prefix", got)
	}
}

func TestCLI_OverrideDatabaseShadowModeFromEnv(t *testing.T) {
	t.Setenv("GO_PARSER_SHADOW_MODE", "false")

	cli, ctx, err := ParseCLI([]string{})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	cfg := DefaultConfig()
	cli.ApplyTo(cfg, ctx)

	if cfg.Database.ShadowMode {
		t.Error("Database.ShadowMode = true, want false from GO_PARSER_SHADOW_MODE")
	}
}

func TestCLI_OverrideServerCeleryQueueName(t *testing.T) {
	cli, ctx, err := ParseCLI([]string{"--server.celery.queue=parser-shadow"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	cfg := DefaultConfig()
	cli.ApplyTo(cfg, ctx)

	if cfg.Server.Celery.Queue != "parser-shadow" {
		t.Errorf("Server.Celery.Queue = %q, want parser-shadow", cfg.Server.Celery.Queue)
	}
}

func TestCLI_ProfileFlags(t *testing.T) {
	cli, _, err := ParseCLI([]string{"--cpuprofile=/tmp/cpu.prof", "--memprofile=/tmp/mem.prof"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if cli.CPUProfile != "/tmp/cpu.prof" {
		t.Errorf("CPUProfile = %q, want /tmp/cpu.prof", cli.CPUProfile)
	}
	if cli.MemProfile != "/tmp/mem.prof" {
		t.Errorf("MemProfile = %q, want /tmp/mem.prof", cli.MemProfile)
	}
}

func TestCLI_Precedence(t *testing.T) {
	// Create a YAML config with specific values
	dir := t.TempDir()
	content := `
pipeline:
  num_workers: 8
server:
  mode: celery
`
	path := filepath.Join(dir, "parser.yaml")
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	// Load YAML config
	cfg, err := LoadConfig(path)
	if err != nil {
		t.Fatalf("unexpected error loading config: %v", err)
	}

	// Parse CLI with override
	cli, ctx, err := ParseCLI([]string{
		"--config-file=" + path,
		"--pipeline.num-workers=32",
	})
	if err != nil {
		t.Fatalf("unexpected error parsing CLI: %v", err)
	}

	// Apply CLI overrides
	cli.ApplyTo(cfg, ctx)

	// CLI should win over YAML for num_workers
	if cfg.Pipeline.NumWorkers != 32 {
		t.Errorf("Pipeline.NumWorkers = %d, want 32 (CLI override)", cfg.Pipeline.NumWorkers)
	}

	// YAML value should be preserved for server.mode (not set on CLI)
	if cfg.Server.Mode != "celery" {
		t.Errorf("Server.Mode = %q, want celery (from YAML, not overridden)", cfg.Server.Mode)
	}
}

func TestCLI_ApplyTo_OnlyExplicitFlags(t *testing.T) {
	cfg := DefaultConfig()
	originalWorkers := cfg.Pipeline.NumWorkers

	// Parse with no flags — nothing should change
	cli, ctx, err := ParseCLI([]string{})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	cli.ApplyTo(cfg, ctx)

	if cfg.Pipeline.NumWorkers != originalWorkers {
		t.Errorf("NumWorkers changed from %d to %d without explicit flag",
			originalWorkers, cfg.Pipeline.NumWorkers)
	}
}

func TestCLI_LocalFlags(t *testing.T) {
	cli, _, err := ParseCLI([]string{
		"--server.mode=local",
		"--server.local.file-path=/path/to/file.txt",
		"--server.local.program=TAN",
		"--server.local.section=1",
		"--server.local.fiscal-year=2024",
		"--server.local.quarter=3",
		"--server.local.program-audit",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if cli.ServerLocalFilePath != "/path/to/file.txt" {
		t.Errorf("FilePath = %q, want /path/to/file.txt", cli.ServerLocalFilePath)
	}
	if cli.ServerLocalProgram != "TAN" {
		t.Errorf("Program = %q, want TAN", cli.ServerLocalProgram)
	}
	if cli.ServerLocalSection != 1 {
		t.Errorf("Section = %d, want 1", cli.ServerLocalSection)
	}
	if cli.ServerLocalFiscalYear != 2024 {
		t.Errorf("FiscalYear = %d, want 2024", cli.ServerLocalFiscalYear)
	}
	if cli.ServerLocalQuarter != 3 {
		t.Errorf("Quarter = %d, want 3", cli.ServerLocalQuarter)
	}
	if !cli.ServerLocalProgramAudit {
		t.Error("ProgramAudit should be true")
	}
}
