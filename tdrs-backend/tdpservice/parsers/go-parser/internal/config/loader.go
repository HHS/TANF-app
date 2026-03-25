package config

import (
	"fmt"
	"log"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
)

// LoadConfig reads the configuration file at the given path, applies
// environment variable interpolation, and returns the merged Config.
//
// The loading sequence implements this precedence (lowest to highest):
//  1. Compiled defaults (DefaultConfig)
//  2. Config file values (parser.yaml)
//  3. Environment variable interpolation (${VAR} in YAML values)
//  4. CLI flag overrides (applied by the caller after LoadConfig returns)
//
// If configFile does not exist, LoadConfig falls back to pipeline.yaml
// in the same directory (for backward compatibility). If neither file
// exists, compiled defaults are returned.
func LoadConfig(configFile string) (*Config, error) {
	data, source, err := readConfigFile(configFile)
	if err != nil {
		return nil, err
	}

	// No config file found — return defaults
	if data == nil {
		return DefaultConfig(), nil
	}

	// If we fell back to pipeline.yaml, use the migration path
	if source == "pipeline" {
		return loadFromPipelineYAML(data)
	}

	// Normal path: interpolate env vars and unmarshal on top of defaults
	data = InterpolateEnvVars(data)

	cfg := DefaultConfig()
	if err := yaml.Unmarshal(data, cfg); err != nil {
		return nil, fmt.Errorf("parsing %s: %w", configFile, err)
	}

	return cfg, nil
}

// readConfigFile tries to read the config file at the given path.
// If it doesn't exist, it falls back to pipeline.yaml in the same directory.
// Returns (data, source, error) where source is "parser" or "pipeline".
func readConfigFile(configFile string) ([]byte, string, error) {
	data, err := os.ReadFile(configFile)
	if err == nil {
		return data, "parser", nil
	}

	if !os.IsNotExist(err) {
		return nil, "", fmt.Errorf("reading %s: %w", configFile, err)
	}

	// Try pipeline.yaml fallback in the same directory
	dir := filepath.Dir(configFile)
	fallback := filepath.Join(dir, "pipeline.yaml")
	data, err = os.ReadFile(fallback)
	if err == nil {
		log.Printf("WARNING: %s not found, falling back to %s. Consider migrating to parser.yaml.", configFile, fallback)
		return data, "pipeline", nil
	}

	if os.IsNotExist(err) {
		return nil, "", nil
	}

	return nil, "", fmt.Errorf("reading %s: %w", fallback, err)
}

// loadFromPipelineYAML reads the legacy pipeline.yaml format and migrates
// it to the new Config structure.
func loadFromPipelineYAML(data []byte) (*Config, error) {
	data = InterpolateEnvVars(data)

	old := DefaultPipelineYAML()
	if err := yaml.Unmarshal(data, old); err != nil {
		return nil, fmt.Errorf("parsing legacy pipeline.yaml: %w", err)
	}

	return migrateFromPipelineYAML(old), nil
}

// migrateFromPipelineYAML converts a legacy PipelineYAML to the new Config.
func migrateFromPipelineYAML(old *PipelineYAML) *Config {
	cfg := DefaultConfig()
	cfg.Pipeline = old.Pipeline
	cfg.Writer = old.Writer
	cfg.Validation.ShortCircuit = old.Validation.ShortCircuit
	cfg.Database.MaxConns = old.Database.MaxConns
	cfg.Database.MinConns = old.Database.MinConns
	cfg.Database.MaxConnLifetime = old.Database.MaxConnLifetime
	cfg.Database.MaxConnIdleTime = old.Database.MaxConnIdleTime
	cfg.Database.HealthCheckPeriod = old.Database.HealthCheckPeriod
	cfg.Storage.Source = old.Reader.Source
	if cfg.Storage.Source == "" {
		cfg.Storage.Source = "local"
	}
	cfg.Storage.S3 = old.Reader.S3
	return cfg
}
