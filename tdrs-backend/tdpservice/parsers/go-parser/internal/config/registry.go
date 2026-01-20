package config

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"

	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/config/validation"
)

// Registry holds all loaded FileSpecs and Schemas.
// It is created once at startup and provides read-only access
// to configuration throughout the application lifetime.
type Registry struct {
	// fileSpecs indexed by "PROGRAM:SECTION" (e.g., "TANF:1")
	fileSpecs map[string]*filespec.FileSpec

	// schemas indexed by path (e.g., "tanf/t1", "common/header")
	schemas map[string]*schema.CompiledSchema

	// defaultMessages indexed by validator ID
	defaultMessages map[string]*validation.DefaultValidatorMessageTemplate

	// metadata holds database info derived from schemas (table names, columns)
	// Built during Load() from YAML schema field definitions
	// See SchemaMetadata type in schema_metadata.go (same package)
	metadata map[string]*DbSchemaMetadata

	// configDir is the root configuration directory
	configDir string
}

// Load reads all configuration files from the given directory and builds the Registry.
// Directory structure expected:
//
//	configDir/
//	├── filespecs/
//	│   ├── tanf_section1.yaml
//	│   ├── tanf_section2.yaml
//	│   └── ...
//	└── schemas/
//	    ├── common/
//	    │   ├── header.yaml
//	    │   └── trailer.yaml
//	    └── tanf/
//	        ├── t1.yaml
//	        ├── t2.yaml
//	        └── t3.yaml
func Load(configDir string) (*Registry, error) {
	r := &Registry{
		fileSpecs: make(map[string]*filespec.FileSpec),
		schemas:   make(map[string]*schema.CompiledSchema),
		defaultMessages: make(map[string]*validation.DefaultValidatorMessageTemplate),
		metadata:  make(map[string]*DbSchemaMetadata),
		configDir: configDir,
	}

	// Load schemas first (FileSpecs reference them)
	if err := r.loadSchemas(); err != nil {
		return nil, fmt.Errorf("loading schemas: %w", err)
	}

	// Load FileSpecs
	if err := r.loadFileSpecs(); err != nil {
		return nil, fmt.Errorf("loading filespecs: %w", err)
	}

	// Validate that all FileSpec schema references are valid
	if err := r.validateReferences(); err != nil {
		return nil, fmt.Errorf("validating references: %w", err)
	}

	// Load default messages
	if err := r.loadDefaultMessages(); err != nil {
		return nil, fmt.Errorf("loading default messages: %w", err)
	}

	// Build database metadata from schema field definitions
	r.buildAllMetadata()

	return r, nil
}

// loadSchemas walks the schemas directory and loads all .yaml files.
func (r *Registry) loadSchemas() error {
	schemasDir := filepath.Join(r.configDir, "schemas")

	return filepath.Walk(schemasDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories and non-YAML files
		if info.IsDir() || !strings.HasSuffix(path, ".yaml") {
			return nil
		}

		// Read and parse the schema file
		data, err := os.ReadFile(path)
		if err != nil {
			return fmt.Errorf("reading %s: %w", path, err)
		}

		var schemaDef schema.SchemaDef
		if err := yaml.Unmarshal(data, &schemaDef); err != nil {
			return fmt.Errorf("parsing %s: %w", path, err)
		}

		// Compute the schema key (relative path without .yaml extension)
		// e.g., "config/schemas/tanf/t1.yaml" -> "tanf/t1"
		relPath, err := filepath.Rel(schemasDir, path)
		if err != nil {
			return fmt.Errorf("computing relative path for %s: %w", path, err)
		}
		key := strings.TrimSuffix(relPath, ".yaml")

		// Compile the schema and set its path
		compiled := schemaDef.Compile()
		compiled.Path = key

		r.schemas[key] = compiled
		return nil
	})
}

// loadFileSpecs reads all .yaml files from the filespecs directory.
func (r *Registry) loadFileSpecs() error {
	filespecsDir := filepath.Join(r.configDir, "filespecs")

	return filepath.Walk(filespecsDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories and non-YAML files
		if info.IsDir() || !strings.HasSuffix(path, ".yaml") {
			return nil
		}

		// Read and parse the file spec file
		data, err := os.ReadFile(path)
		if err != nil {
			return fmt.Errorf("reading %s: %w", path, err)
		}

		var specDef filespec.FileSpec
		if err := yaml.Unmarshal(data, &specDef); err != nil {
			return fmt.Errorf("parsing %s: %w", path, err)
		}

		// Index by "PROGRAM:SECTION"
		key := fmt.Sprintf("%s:%d", specDef.Program, specDef.Section)
		r.fileSpecs[key] = &specDef

		return nil
	})
}

// loadDefaultMessages reads the validation/messages.yaml file.
func (r *Registry) loadDefaultMessages() error {
	defaultMessagesPath := filepath.Join(r.configDir, "validation/messages.yaml")

	// Read and parse the default message templates
	data, err := os.ReadFile(defaultMessagesPath)
	if err != nil {
		return fmt.Errorf("reading %s: %w", defaultMessagesPath, err)
	}

	var specDef validation.DefaultMessageTemplates
	if err := yaml.Unmarshal(data, &specDef); err != nil {
		return fmt.Errorf("parsing %s: %w", defaultMessagesPath, err)
	}

	// Index by validator ID
	for _, validator := range specDef.Validators {
		r.defaultMessages[validator.ID] = &validator
	}

	return nil
}

// validateReferences ensures all schema references in FileSpecs point to loaded schemas.
func (r *Registry) validateReferences() error {
	for specKey, spec := range r.fileSpecs {
		// Validate schemas list
		for _, schemaPath := range spec.Schemas {
			if _, ok := r.schemas[schemaPath]; !ok {
				return fmt.Errorf("filespec %s references unknown schema: %s", specKey, schemaPath)
			}
		}

		// Validate record_type_detection prefixes
		for _, prefix := range spec.RecordTypeDetection.Prefixes {
			if _, ok := r.schemas[prefix.Schema]; !ok {
				return fmt.Errorf("filespec %s prefix %q references unknown schema: %s",
					specKey, prefix.Prefix, prefix.Schema)
			}
		}

		// Validate grouped_schemas
		for _, schemaPath := range spec.Accumulator.GroupedSchemas {
			if _, ok := r.schemas[schemaPath]; !ok {
				return fmt.Errorf("filespec %s grouped_schemas references unknown schema: %s",
					specKey, schemaPath)
			}
		}
	}

	return nil
}

// GetFileSpec returns the FileSpec for the given program and section.
// Returns nil if not found.
func (r *Registry) GetFileSpec(program string, section int) *filespec.FileSpec {
	key := fmt.Sprintf("%s:%d", program, section)
	return r.fileSpecs[key]
}

// GetSchema returns a compiled schema by its path (e.g., "tanf/t1").
// Returns nil if not found.
func (r *Registry) GetSchema(path string) *schema.CompiledSchema {
	return r.schemas[path]
}

// MustGetSchema returns a compiled schema by path, panicking if not found.
// Use this only when you're certain the schema exists (e.g., after validation).
func (r *Registry) MustGetSchema(path string) *schema.CompiledSchema {
	s := r.schemas[path]
	if s == nil {
		panic(fmt.Sprintf("schema not found: %s", path))
	}
	return s
}

// ListFileSpecs returns all loaded FileSpec keys (e.g., ["TANF:1", "TANF:2", ...]).
func (r *Registry) ListFileSpecs() []string {
	keys := make([]string, 0, len(r.fileSpecs))
	for k := range r.fileSpecs {
		keys = append(keys, k)
	}
	return keys
}

// ListSchemas returns all loaded schema paths (e.g., ["tanf/t1", "common/header", ...]).
func (r *Registry) ListSchemas() []string {
	keys := make([]string, 0, len(r.schemas))
	for k := range r.schemas {
		keys = append(keys, k)
	}
	return keys
}

//
func (r *Registry) GetDefaultMessageTempates() map[string]*validation.DefaultValidatorMessageTemplate {
	return r.defaultMessages
}

// Stats returns statistics about loaded configuration.
func (r *Registry) Stats() (numFileSpecs, numSchemas, numDefaultMessages int) {
	return len(r.fileSpecs), len(r.schemas), len(r.defaultMessages)
}
