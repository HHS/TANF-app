package config

import (
	"fmt"
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
// If the config file does not exist, compiled defaults are returned.
func LoadConfig(configFile string) (*Config, error) {
	data, err := os.ReadFile(configFile)
	if err != nil {
		if os.IsNotExist(err) {
			return DefaultConfig(), nil
		}
		return nil, fmt.Errorf("reading %s: %w", configFile, err)
	}

	data = InterpolateEnvVars(data)

	cfg := DefaultConfig()
	if err := yaml.Unmarshal(data, cfg); err != nil {
		return nil, fmt.Errorf("parsing %s: %w", configFile, err)
	}

	// If config_dir is relative, resolve it to an absolute path based on the
	// config file's parent directory. The config file (parser.yaml) lives inside
	// config_dir, so its parent directory IS config_dir. This allows the parser
	// and other commands to work regardless of the working directory when an
	// absolute config file path is provided.
	if !filepath.IsAbs(cfg.Global.ConfigDir) {
		absConfigFile, err := filepath.Abs(configFile)
		if err != nil {
			return nil, fmt.Errorf("resolving config file path: %w", err)
		}
		cfg.Global.ConfigDir = filepath.Dir(absConfigFile)
	}

	return cfg, nil
}
