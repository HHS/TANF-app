package validation

import (
	"bytes"
	"text/template"
)

// Error type constants
const (
	ErrorTypeRecordPreCheck   = "RECORD_PRE_CHECK"
	ErrorTypeFieldValue       = "FIELD_VALUE"
	ErrorTypeValueConsistency = "VALUE_CONSISTENCY"
	ErrorTypeCaseConsistency  = "CASE_CONSISTENCY"
)

// Scope constants
const (
	ScopeField  = "field"
	ScopeRecord = "record"
	ScopeGroup  = "group"
)

// ValidationResult represents the outcome of a single validator execution.
type ValidationResult struct {
	Valid       bool
	Category    int    // Legacy: kept for backward compatibility
	ErrorType   string // The actual error type for serialization decisions
	ValidatorID string
	FieldName   string // Only set for field-scope errors
	LineNumber  int    // For per-record attribution in group validators
	RecordType  string // For per-record attribution in group validators
	Error       error  // Set if expression evaluation failed
	Validator   *CompiledValidator
}

// BlocksRecord returns true if this error type blocks record serialization.
func (vr *ValidationResult) BlocksRecord() bool {
	return vr.ErrorType == ErrorTypeRecordPreCheck
}

// BlocksGroup returns true if this error type blocks group serialization.
func (vr *ValidationResult) BlocksGroup() bool {
	return vr.ErrorType == ErrorTypeCaseConsistency
}

// Message generates the error message for this validation result.
// Context provides template variables (RecordType, Item, Value, etc.).
func (vr *ValidationResult) Message(ctx map[string]any) string {
	if vr.Valid || vr.Validator == nil || vr.Validator.Message == nil {
		return ""
	}
	var buf bytes.Buffer
	if err := vr.Validator.Message.Execute(&buf, ctx); err != nil {
		return vr.ValidatorID + ": template error: " + err.Error()
	}
	return buf.String()
}

// RecordValidationResult contains all validation results for a single record.
type RecordValidationResult struct {
	Record          Record
	Cat1Errors      []*ValidationResult // Legacy: RECORD_PRE_CHECK errors
	Cat2Errors      []*ValidationResult // Legacy: FIELD_VALUE errors
	Cat3Errors      []*ValidationResult // Legacy: VALUE_CONSISTENCY errors
	RecordErrors    []*ValidationResult // All record-scope errors (new)
	FieldErrors     []*ValidationResult // All field-scope errors (new)
	Skipped         bool                // True if field/record validators were skipped due to blocking errors
}

// HasErrors returns true if this record has any validation errors.
func (rvr *RecordValidationResult) HasErrors() bool {
	return len(rvr.Cat1Errors) > 0 || len(rvr.Cat2Errors) > 0 || len(rvr.Cat3Errors) > 0 ||
		len(rvr.RecordErrors) > 0 || len(rvr.FieldErrors) > 0
}

// HasCat1Errors returns true if this record has category 1 errors.
// Records with Cat1 errors should not be serialized to the database.
// Deprecated: Use HasBlockingErrors() instead.
func (rvr *RecordValidationResult) HasCat1Errors() bool {
	return len(rvr.Cat1Errors) > 0
}

// HasBlockingErrors returns true if this record has errors that block serialization.
// This checks for RECORD_PRE_CHECK errors.
func (rvr *RecordValidationResult) HasBlockingErrors() bool {
	// Check legacy Cat1Errors
	if len(rvr.Cat1Errors) > 0 {
		return true
	}
	// Check new RecordErrors for blocking types
	for _, err := range rvr.RecordErrors {
		if err.BlocksRecord() {
			return true
		}
	}
	return false
}

// ShouldSerialize returns true if this record should be written to the database.
// Records with blocking errors are rejected and should not be serialized.
func (rvr *RecordValidationResult) ShouldSerialize() bool {
	return !rvr.HasBlockingErrors()
}

// AllErrors returns all errors from all categories.
func (rvr *RecordValidationResult) AllErrors() []*ValidationResult {
	total := len(rvr.Cat1Errors) + len(rvr.Cat2Errors) + len(rvr.Cat3Errors) +
		len(rvr.RecordErrors) + len(rvr.FieldErrors)
	if total == 0 {
		return nil
	}
	result := make([]*ValidationResult, 0, total)
	result = append(result, rvr.Cat1Errors...)
	result = append(result, rvr.Cat2Errors...)
	result = append(result, rvr.Cat3Errors...)
	result = append(result, rvr.RecordErrors...)
	result = append(result, rvr.FieldErrors...)
	return result
}

// GroupValidationResult contains all validation results for a group (case).
type GroupValidationResult struct {
	Group         WrappedGroup
	Cat4Errors    []*ValidationResult   // Legacy: CASE_CONSISTENCY errors
	GroupErrors   []*ValidationResult   // All group-scope errors (new)
	RecordResults []*RecordValidationResult
}

// HasErrors returns true if this group has any validation errors.
func (gvr *GroupValidationResult) HasErrors() bool {
	if len(gvr.Cat4Errors) > 0 || len(gvr.GroupErrors) > 0 {
		return true
	}
	for _, rr := range gvr.RecordResults {
		if rr.HasErrors() {
			return true
		}
	}
	return false
}

// HasCat4Errors returns true if this group has category 4 errors.
// Groups with Cat4 errors should not be serialized to the database.
// Deprecated: Use HasBlockingGroupErrors() instead.
func (gvr *GroupValidationResult) HasCat4Errors() bool {
	return len(gvr.Cat4Errors) > 0
}

// HasBlockingGroupErrors returns true if this group has errors that block serialization.
// This checks for CASE_CONSISTENCY errors.
func (gvr *GroupValidationResult) HasBlockingGroupErrors() bool {
	// Check legacy Cat4Errors
	if len(gvr.Cat4Errors) > 0 {
		return true
	}
	// Check new GroupErrors for blocking types
	for _, err := range gvr.GroupErrors {
		if err.BlocksGroup() {
			return true
		}
	}
	return false
}

// ShouldSerialize returns true if this group should be written to the database.
// Groups with blocking errors are rejected and should not be serialized.
func (gvr *GroupValidationResult) ShouldSerialize() bool {
	return !gvr.HasBlockingGroupErrors()
}

// GetSerializableRecordResults returns only the record results that should be serialized.
// Records with blocking errors are filtered out.
func (gvr *GroupValidationResult) GetSerializableRecordResults() []*RecordValidationResult {
	if gvr.HasBlockingGroupErrors() {
		return nil // Entire group is rejected
	}
	var results []*RecordValidationResult
	for _, rr := range gvr.RecordResults {
		if rr.ShouldSerialize() {
			results = append(results, rr)
		}
	}
	return results
}

// AllRecordErrors returns all record-level errors from this group.
func (gvr *GroupValidationResult) AllRecordErrors() []*ValidationResult {
	var result []*ValidationResult
	for _, rr := range gvr.RecordResults {
		result = append(result, rr.AllErrors()...)
	}
	return result
}

// AllGroupErrors returns all group-level errors (both legacy and new).
func (gvr *GroupValidationResult) AllGroupErrors() []*ValidationResult {
	total := len(gvr.Cat4Errors) + len(gvr.GroupErrors)
	if total == 0 {
		return nil
	}
	result := make([]*ValidationResult, 0, total)
	result = append(result, gvr.Cat4Errors...)
	result = append(result, gvr.GroupErrors...)
	return result
}

// TotalErrorCount returns the total number of errors across all categories.
func (gvr *GroupValidationResult) TotalErrorCount() int {
	count := len(gvr.Cat4Errors) + len(gvr.GroupErrors)
	for _, rr := range gvr.RecordResults {
		count += len(rr.Cat1Errors) + len(rr.Cat2Errors) + len(rr.Cat3Errors) +
			len(rr.RecordErrors) + len(rr.FieldErrors)
	}
	return count
}

// AddRecordError adds an error attributed to a specific record from a group-scope validator.
// This is used for per_record result mode group validators.
func (gvr *GroupValidationResult) AddRecordError(rec Record, cv *CompiledValidator, err error) {
	// Find the matching RecordValidationResult
	for _, rr := range gvr.RecordResults {
		if rr.Record.GetLineNumber() == rec.GetLineNumber() {
			vr := &ValidationResult{
				Valid:       false,
				ErrorType:   cv.ErrorType,
				ValidatorID: cv.ID,
				LineNumber:  rec.GetLineNumber(),
				RecordType:  rec.GetRecordType(),
				Error:       err,
				Validator:   cv,
			}
			rr.RecordErrors = append(rr.RecordErrors, vr)
			return
		}
	}
}

// validResultSingleton is reused for successful validations to reduce allocations.
var validResultSingleton = &ValidationResult{Valid: true}

// CompiledExpr is shared across validators with identical expressions.
type CompiledExpr struct {
	Expr    string
	Program any // *vm.Program from expr package
}

// CompiledValidator is per-use-site (resolved message at compile time).
type CompiledValidator struct {
	ID         string
	Category   int                // Legacy: kept for backward compatibility
	Scope      string             // "field", "record", or "group"
	ErrorType  string             // The declared error type (or default based on scope)
	ResultMode string             // "single" (default) or "per_record" (for group validators)
	Expr       *CompiledExpr      // Pointer to shared compiled expr
	Message    *template.Template // Pre-resolved (default or override)
	Fields     []string           // Fields involved (for record/group validators)
	Params     map[string]any     // Runtime params for expressions (e.g., {n: 9})
}
