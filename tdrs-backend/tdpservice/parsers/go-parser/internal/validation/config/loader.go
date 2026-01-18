// Package config provides YAML configuration loading for the validation system.
package config

import (
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"

	"go-parser/internal/schema"
	"go-parser/internal/validation"
	"go-parser/internal/validation/registry"
)

// SchemaValidationConfig represents the validation section of a schema YAML file.
type SchemaValidationConfig struct {
	Category1 []validation.ValidatorConfig `yaml:"category1,omitempty"`
	Category3 []validation.ValidatorConfig `yaml:"category3,omitempty"`
}

// FieldValidationConfig represents the validation config for a field.
type FieldValidationConfig struct {
	Name      string                       `yaml:"name"`
	Category2 []validation.ValidatorConfig `yaml:"category2,omitempty"`
}

// SchemaConfigWithValidation represents a full schema config with validation.
type SchemaConfigWithValidation struct {
	RecordType string                    `yaml:"record_type"`
	Fields     []FieldValidationConfig   `yaml:"fields,omitempty"`
	Shared     []FieldValidationConfig   `yaml:"shared,omitempty"`
	Segments   []SegmentValidationConfig `yaml:"segments,omitempty"`

	// Direct validation sections (for non-field validators)
	Category1 []validation.ValidatorConfig `yaml:"category1,omitempty"`
	Category3 []validation.ValidatorConfig `yaml:"category3,omitempty"`
}

// SegmentValidationConfig represents a segment with validation.
type SegmentValidationConfig struct {
	Fields []FieldValidationConfig `yaml:"fields,omitempty"`
}

// FileSpecValidationConfig represents the validation section of a filespec YAML file.
type FileSpecValidationConfig struct {
	Category4 []validation.ValidatorConfig `yaml:"category4,omitempty"`
}

// OrchestratorConfigFile represents the orchestrator config file format.
type OrchestratorConfigFile struct {
	Categories     []validation.CategoryConfig   `yaml:"categories"`
	ExecutionOrder []int                         `yaml:"execution_order"`
	ShortCircuit   []validation.ShortCircuitRule `yaml:"short_circuit"`
}

// MessagesConfigFile represents the messages config file format.
type MessagesConfigFile struct {
	Validators map[string]string `yaml:"validators"`
	Overrides  map[string]string `yaml:"overrides,omitempty"`
}

// Loader loads validation configuration from YAML files.
type Loader struct {
	registry *registry.ValidatorRegistry
	messages *registry.MessageRegistry
}

// NewLoader creates a new config loader.
func NewLoader(validatorReg *registry.ValidatorRegistry, messageReg *registry.MessageRegistry) *Loader {
	return &Loader{
		registry: validatorReg,
		messages: messageReg,
	}
}

// LoadOrchestratorConfig loads orchestrator configuration from a YAML file.
func (l *Loader) LoadOrchestratorConfig(path string) (*validation.OrchestratorConfig, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("reading orchestrator config: %w", err)
	}

	var file OrchestratorConfigFile
	if err := yaml.Unmarshal(data, &file); err != nil {
		return nil, fmt.Errorf("parsing orchestrator config: %w", err)
	}

	return &validation.OrchestratorConfig{
		Categories:     file.Categories,
		ExecutionOrder: file.ExecutionOrder,
		ShortCircuit:   file.ShortCircuit,
	}, nil
}

// LoadMessagesConfig loads message templates from a YAML file.
func (l *Loader) LoadMessagesConfig(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("reading messages config: %w", err)
	}

	var file MessagesConfigFile
	if err := yaml.Unmarshal(data, &file); err != nil {
		return fmt.Errorf("parsing messages config: %w", err)
	}

	// Register default templates
	for validatorID, template := range file.Validators {
		if err := l.messages.RegisterDefault(validatorID, template); err != nil {
			return fmt.Errorf("registering message for %s: %w", validatorID, err)
		}
	}

	// Register overrides
	for key, template := range file.Overrides {
		if err := l.messages.RegisterOverride(key, template); err != nil {
			return fmt.Errorf("registering override for %s: %w", key, err)
		}
	}

	return nil
}

// LoadSchemaValidators loads validators from a schema YAML file.
func (l *Loader) LoadSchemaValidators(path string, compiledSchema *schema.CompiledSchema) (*validation.SchemaValidators, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("reading schema config: %w", err)
	}

	var config SchemaConfigWithValidation
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("parsing schema config: %w", err)
	}

	validators := validation.NewSchemaValidators()

	// Build Cat 1 validators
	cat1, err := l.registry.BuildAll(config.Category1)
	if err != nil {
		return nil, fmt.Errorf("building cat1 validators: %w", err)
	}
	validators.Cat1 = cat1

	// Build Cat 3 validators
	cat3, err := l.registry.BuildAll(config.Category3)
	if err != nil {
		return nil, fmt.Errorf("building cat3 validators: %w", err)
	}
	validators.Cat3 = cat3

	// Build Cat 2 validators from shared fields
	for _, fieldConfig := range config.Shared {
		if len(fieldConfig.Category2) == 0 {
			continue
		}
		fieldIndex, ok := compiledSchema.FieldIndex[fieldConfig.Name]
		if !ok {
			continue // Field not in schema
		}
		cat2, err := l.registry.BuildAll(fieldConfig.Category2)
		if err != nil {
			return nil, fmt.Errorf("building cat2 validators for %s: %w", fieldConfig.Name, err)
		}
		validators.Cat2[fieldIndex] = cat2
	}

	// Build Cat 2 validators from segment fields (use first segment)
	if len(config.Segments) > 0 {
		for _, fieldConfig := range config.Segments[0].Fields {
			if len(fieldConfig.Category2) == 0 {
				continue
			}
			fieldIndex, ok := compiledSchema.FieldIndex[fieldConfig.Name]
			if !ok {
				continue
			}
			cat2, err := l.registry.BuildAll(fieldConfig.Category2)
			if err != nil {
				return nil, fmt.Errorf("building cat2 validators for %s: %w", fieldConfig.Name, err)
			}
			validators.Cat2[fieldIndex] = cat2
		}
	}

	// Also handle flat "fields" section
	for _, fieldConfig := range config.Fields {
		if len(fieldConfig.Category2) == 0 {
			continue
		}
		fieldIndex, ok := compiledSchema.FieldIndex[fieldConfig.Name]
		if !ok {
			continue
		}
		cat2, err := l.registry.BuildAll(fieldConfig.Category2)
		if err != nil {
			return nil, fmt.Errorf("building cat2 validators for %s: %w", fieldConfig.Name, err)
		}
		validators.Cat2[fieldIndex] = cat2
	}

	return validators, nil
}

// LoadFileSpecValidators loads Cat 4 validators from a filespec YAML file.
func (l *Loader) LoadFileSpecValidators(path string) (*validation.FileSpecValidators, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("reading filespec config: %w", err)
	}

	var config FileSpecValidationConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("parsing filespec config: %w", err)
	}

	cat4, err := l.registry.BuildAll(config.Category4)
	if err != nil {
		return nil, fmt.Errorf("building cat4 validators: %w", err)
	}

	return &validation.FileSpecValidators{
		Cat4: cat4,
	}, nil
}

// LoadAllConfigs loads all validation configs from a config directory.
// Expected structure:
//
//	configDir/
//	  validation/
//	    orchestrator.yaml
//	    messages.yaml
//	  schemas/
//	    tanf/t1.yaml
//	    ...
//	  filespecs/
//	    tanf/s1.yaml
//	    ...
func (l *Loader) LoadAllConfigs(configDir string) (*validation.OrchestratorConfig, error) {
	validationDir := filepath.Join(configDir, "validation")

	// Load orchestrator config
	orchPath := filepath.Join(validationDir, "orchestrator.yaml")
	orchConfig, err := l.LoadOrchestratorConfig(orchPath)
	if err != nil {
		// Use defaults if not found
		if os.IsNotExist(err) {
			orchConfig = validation.DefaultOrchestratorConfig()
		} else {
			return nil, err
		}
	}

	// Load messages config
	messagesPath := filepath.Join(validationDir, "messages.yaml")
	if err := l.LoadMessagesConfig(messagesPath); err != nil {
		if !os.IsNotExist(err) {
			return nil, err
		}
		// Use built-in defaults if not found
		registry.RegisterBuiltinMessages(l.messages)
	}

	return orchConfig, nil
}

// BuildValidatorConfigFromMap converts a map to ValidatorConfig.
// Useful for building configs programmatically.
func BuildValidatorConfigFromMap(m map[string]any) (validation.ValidatorConfig, error) {
	data, err := yaml.Marshal(m)
	if err != nil {
		return validation.ValidatorConfig{}, err
	}

	var config validation.ValidatorConfig
	if err := yaml.Unmarshal(data, &config); err != nil {
		return validation.ValidatorConfig{}, err
	}

	return config, nil
}
