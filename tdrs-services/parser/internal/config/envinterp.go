package config

import (
	"os"
	"regexp"
)

// envVarPattern matches ${VAR_NAME} patterns in config files.
var envVarPattern = regexp.MustCompile(`\$\{([A-Za-z_][A-Za-z0-9_]*)\}`)

// InterpolateEnvVars replaces ${VAR_NAME} patterns in raw YAML bytes
// with the corresponding environment variable values. Variables that
// are not set in the environment are replaced with an empty string.
//
// Only the ${VAR} syntax is supported — bare $VAR references and
// malformed patterns like ${} are left untouched.
func InterpolateEnvVars(data []byte) []byte {
	return envVarPattern.ReplaceAllFunc(data, func(match []byte) []byte {
		varName := envVarPattern.FindSubmatch(match)[1]
		return []byte(os.Getenv(string(varName)))
	})
}
