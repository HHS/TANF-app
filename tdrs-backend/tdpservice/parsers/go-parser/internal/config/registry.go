package config

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"

	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
)

// Registry holds all loaded FileSpecs, and Schemas.
// It is created once at startup and provides read-only access
// to configuration throughout the application lifetime.
type Registry struct {
	// fileSpecs indexed by "PROGRAM:SECTION" (e.g., "TANF:1")
	fileSpecs map[string]*filespec.FileSpec

	// schemas indexed by path (e.g., "tanf/t1", "common/header")
	schemas map[string]*schema.CompiledSchema

	// metadata holds database info derived from schemas (table names, columns)
	// Built during Load() from YAML schema field definitions
	// See SchemaMetadata type in schema_metadata.go (same package)
	metadata map[string]*DbSchemaMetadata

	// configDir is the root configuration directory
	configDir string
}

// LoadFromFiles builds a Registry from explicit file lists. The schemaFiles and
// filespecFiles should be absolute paths (already resolved from glob patterns).
// The schemasBaseDir is used to compute schema keys as relative paths.
//
// This is the primary loading method used by the new config system. It accepts
// pre-resolved file paths instead of walking hardcoded directories.
func LoadFromFiles(schemaFiles, filespecFiles []string, schemasBaseDir, configDir string) (*Registry, error) {
	r := &Registry{
		fileSpecs: make(map[string]*filespec.FileSpec),
		schemas:   make(map[string]*schema.CompiledSchema),
		metadata:  make(map[string]*DbSchemaMetadata),
		configDir: configDir,
	}

	for _, path := range schemaFiles {
		if err := r.loadSchemaFile(path, schemasBaseDir); err != nil {
			return nil, fmt.Errorf("loading schema %s: %w", path, err)
		}
	}

	for _, path := range filespecFiles {
		if err := r.loadFileSpecFile(path); err != nil {
			return nil, fmt.Errorf("loading filespec %s: %w", path, err)
		}
	}

	if err := r.validateReferences(); err != nil {
		return nil, fmt.Errorf("validating references: %w", err)
	}

	r.buildAllMetadata()
	return r, nil
}

// Load reads all configuration files from the given directory and builds the Registry.
// This is a backward-compatible wrapper around LoadFromFiles that walks the default
// schemas/ and filespecs/ directories.
//
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
	schemasDir := filepath.Join(configDir, "schemas")
	filespecsDir := filepath.Join(configDir, "filespecs")

	schemaFiles, err := collectYAMLFiles(schemasDir)
	if err != nil {
		return nil, fmt.Errorf("collecting schema files: %w", err)
	}

	filespecFiles, err := collectYAMLFiles(filespecsDir)
	if err != nil {
		return nil, fmt.Errorf("collecting filespec files: %w", err)
	}

	return LoadFromFiles(schemaFiles, filespecFiles, schemasDir, configDir)
}

// collectYAMLFiles walks a directory and returns all .yaml file paths.
func collectYAMLFiles(dir string) ([]string, error) {
	var files []string
	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && strings.HasSuffix(path, ".yaml") {
			files = append(files, path)
		}
		return nil
	})
	return files, err
}

// loadSchemaFile reads, parses, and compiles a single schema YAML file.
// The key is derived from the file's path relative to schemasBaseDir.
func (r *Registry) loadSchemaFile(path, schemasBaseDir string) error {
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
	relPath, err := filepath.Rel(schemasBaseDir, path)
	if err != nil {
		return fmt.Errorf("computing relative path for %s: %w", path, err)
	}
	key := strings.TrimSuffix(relPath, ".yaml")

	compiled := schemaDef.Compile()
	compiled.Path = key
	r.schemas[key] = compiled
	return nil
}

// loadFileSpecFile reads and parses a single filespec YAML file.
func (r *Registry) loadFileSpecFile(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("reading %s: %w", path, err)
	}

	var specDef filespec.FileSpec
	if err := yaml.Unmarshal(data, &specDef); err != nil {
		return fmt.Errorf("parsing %s: %w", path, err)
	}

	key := fmt.Sprintf("%s:%d", specDef.Program, specDef.Section)
	r.fileSpecs[key] = &specDef
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

// Schemas returns the loaded schemas map.
func (r *Registry) Schemas() map[string]*schema.CompiledSchema {
	return r.schemas
}

// FileSpecs returns the loaded filespecs map.
func (r *Registry) FileSpecs() map[string]*filespec.FileSpec {
	return r.fileSpecs
}

// ConfigDir returns the root configuration directory.
func (r *Registry) ConfigDir() string {
	return r.configDir
}

// Stats returns statistics about loaded configuration.
func (r *Registry) Stats() (numFileSpecs, numSchemas int) {
	return len(r.fileSpecs), len(r.schemas)
}

// NewTestRegistry creates a minimal Registry for unit testing.
// Only schemas are populated; fileSpecs are empty.
func NewTestRegistry(schemas map[string]*schema.CompiledSchema) *Registry {
	return &Registry{
		fileSpecs: make(map[string]*filespec.FileSpec),
		schemas:   schemas,
		metadata:  make(map[string]*DbSchemaMetadata),
	}
}

// LoadContentTypes loads Django content type IDs from the provided map and sets them on schema metadata.
// The map should be keyed by model name (e.g., "tanf_t1") with content type ID as value.
// This is typically called once after loading the registry, using data queried from django_content_type.
// Content types are used to link parser errors to their corresponding record models.
func (r *Registry) LoadContentTypes(contentTypes map[string]int32) {
	r.SetContentTypeIDs(contentTypes)
}
