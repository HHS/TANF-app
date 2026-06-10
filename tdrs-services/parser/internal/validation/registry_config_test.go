package validation

import (
	"os"
	"path/filepath"
	"testing"

	"go-parser/internal/config"
)

func productionConfigDir(t *testing.T) string {
	t.Helper()

	dir := filepath.Join("..", "..", "config")
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		t.Fatal("real config directory not found -- tests must run from go-parser root")
	}

	return dir
}

func TestProductionValidators_LoadAndCompile(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Global.ConfigDir = productionConfigDir(t)

	reg, err := config.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("config.NewRegistry failed: %v", err)
	}

	validators, err := NewRegistry(cfg, reg)
	if err != nil {
		t.Fatalf("validation.NewRegistry failed: %v", err)
	}

	if validators == nil {
		t.Fatal("expected validator registry to be initialized")
	}
}
