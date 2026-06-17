package local

import (
	"context"
	"os"
	"strings"
	"testing"

	"go-parser/internal/config"
)

func TestNew_Construction(t *testing.T) {
	cfg := config.DefaultConfig()

	m := New(cfg, nil, nil)

	if m == nil {
		t.Fatal("New returned nil")
	}
	if m.Config != cfg {
		t.Error("cfg not set correctly")
	}
}

func TestNeedsDatabase_FileMode(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Writer.Mode = "file"
	m := New(cfg, nil, nil)

	if m.needsDatabase() {
		t.Error("file mode should not need database")
	}
}

func TestNeedsDatabase_DatabaseMode(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Writer.Mode = "database"
	m := New(cfg, nil, nil)

	if !m.needsDatabase() {
		t.Error("database mode should need database")
	}
}

func TestNeedsDatabase_DefaultMode(t *testing.T) {
	cfg := config.DefaultConfig()
	// Default writer mode is "database"
	m := New(cfg, nil, nil)

	if !m.needsDatabase() {
		t.Error("default mode should need database")
	}
}

func TestDataFileTableNameUsesConfiguredShadowMode(t *testing.T) {
	t.Run("shadow mode", func(t *testing.T) {
		cfg := config.DefaultConfig()
		cfg.Database.ShadowMode = true
		cfg.Database.TablePrefix = config.DefaultTablePrefix

		m := New(cfg, nil, nil)

		if got := m.dataFileTableName(); got != "shadow_data_files_datafile" {
			t.Fatalf("dataFileTableName() = %q, want shadow_data_files_datafile", got)
		}
	})

	t.Run("production mode", func(t *testing.T) {
		cfg := config.DefaultConfig()
		cfg.Database.ShadowMode = false
		cfg.Database.TablePrefix = config.DefaultTablePrefix

		m := New(cfg, nil, nil)

		if got := m.dataFileTableName(); got != "data_files_datafile" {
			t.Fatalf("dataFileTableName() = %q, want data_files_datafile", got)
		}
	})
}

func TestRun_MissingFilePath(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Writer.Mode = "file"
	cfg.Server.Local.FilePath = ""
	cfg.Server.Local.Program = "TAN"
	cfg.Server.Local.Section = 1

	m := New(cfg, nil, nil)
	err := m.Run(context.Background())

	if err == nil {
		t.Fatal("expected error for missing file path")
	}
	if !strings.Contains(err.Error(), "server.local.file-path") {
		t.Errorf("error = %q, should mention server.local.file-path", err.Error())
	}
}

func TestRun_MissingProgram(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Writer.Mode = "file"
	cfg.Server.Local.FilePath = "/some/path"
	cfg.Server.Local.Program = ""
	cfg.Server.Local.Section = 1

	m := New(cfg, nil, nil)
	err := m.Run(context.Background())

	if err == nil {
		t.Fatal("expected error for missing program")
	}
	if !strings.Contains(err.Error(), "server.local.program") {
		t.Errorf("error = %q, should mention server.local.program", err.Error())
	}
}

func TestRun_MissingSection(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Writer.Mode = "file"
	cfg.Server.Local.FilePath = "/some/path"
	cfg.Server.Local.Program = "TAN"
	cfg.Server.Local.Section = 0

	m := New(cfg, nil, nil)
	err := m.Run(context.Background())

	if err == nil {
		t.Fatal("expected error for missing section")
	}
	if !strings.Contains(err.Error(), "server.local.section") {
		t.Errorf("error = %q, should mention server.local.section", err.Error())
	}
}

func TestRun_NonExistentFile(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Writer.Mode = "file"
	cfg.Server.Local.FilePath = "/nonexistent/path/file.txt"
	cfg.Server.Local.Program = "TAN"
	cfg.Server.Local.Section = 1
	cfg.Server.Local.FiscalYear = 2024
	cfg.Server.Local.Quarter = 1

	cfg.SchemaFiles = nil
	cfg.FilespecFiles = nil
	cfg.Global.ConfigDir = t.TempDir()
	reg, err := config.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("NewRegistry failed: %v", err)
	}

	m := New(cfg, reg, nil)
	err = m.Run(context.Background())

	if err == nil {
		t.Fatal("expected error for non-existent file")
	}
	if !strings.Contains(err.Error(), "failed to open file") {
		t.Errorf("error = %q, should mention failed to open file", err.Error())
	}
}

func TestRun_MissingFileSpec(t *testing.T) {
	// Create a temp file so file open succeeds, but registry has no matching spec
	tmpDir := t.TempDir()
	tmpFile := tmpDir + "/test.txt"
	if err := os.WriteFile(tmpFile, []byte("HEADER dummy data\n"), 0o644); err != nil {
		t.Fatalf("Failed to create test file: %v", err)
	}

	cfg := config.DefaultConfig()
	cfg.Writer.Mode = "file"
	cfg.Writer.OutputDir = tmpDir + "/output"
	cfg.Server.Local.FilePath = tmpFile
	cfg.Server.Local.Program = "NONEXISTENT"
	cfg.Server.Local.Section = 99
	cfg.Server.Local.FiscalYear = 2024
	cfg.Server.Local.Quarter = 1
	cfg.SchemaFiles = nil
	cfg.FilespecFiles = nil
	cfg.Global.ConfigDir = t.TempDir()

	reg, err := config.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("NewRegistry failed: %v", err)
	}

	m := New(cfg, reg, nil)
	err = m.Run(context.Background())

	if err == nil {
		t.Fatal("expected error for missing file spec")
	}
	if !strings.Contains(err.Error(), "no file spec") {
		t.Errorf("error = %q, should mention no file spec", err.Error())
	}
}

func TestErrRequired(t *testing.T) {
	err := errRequired("some.field")
	expected := "some.field is required in local mode"
	if err.Error() != expected {
		t.Errorf("errRequired = %q, want %q", err.Error(), expected)
	}
}
