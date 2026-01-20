// Package validation provides a config-driven validation system for parsed records.
// It supports multiple validation categories (Cat 1-4), composable validators,
// and lazy error message generation.
package validation

import (
	"go-parser/internal/parser"
	"go-parser/internal/validation/registry"
)

// GroupValidationResult holds the results of validating an entire group.
type GroupValidationResult struct {
	// Rejected is true if the entire group was rejected (e.g., Cat 4 failure).
	Rejected bool

	// ValidRecords are records that passed all validations.
	ValidRecords []*parser.ParsedRecord

	// RejectedRecords are records that failed validation (for error logging).
	RejectedRecords []*parser.ParsedRecord

	// Errors are all validation failures, used for lazy error generation.
	Errors []*registry.ValidationResult
}
