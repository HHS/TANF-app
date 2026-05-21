package validation

import (
	"bytes"
	"sync"
	"text/template"

	"go-parser/internal/parser"
)

// Error type constants
const (
	ErrorTypePreCheck         = "PRE_CHECK"
	ErrorTypeRecordPreCheck   = "RECORD_PRE_CHECK"
	ErrorTypeFieldValue       = "FIELD_VALUE"
	ErrorTypeValueConsistency = "VALUE_CONSISTENCY"
	ErrorTypeCaseConsistency  = "CASE_CONSISTENCY"
)

// bufPool provides reusable bytes.Buffer instances for message rendering.
// This reduces allocations when generating error messages.
var bufPool = sync.Pool{
	New: func() any {
		return new(bytes.Buffer)
	},
}

// Scope constants
const (
	ScopeField  = "field"
	ScopeRecord = "record"
	ScopeGroup  = "group"
)

// ValidationResult represents the outcome of a single validator execution.
type ValidationResult struct {
	Valid           bool
	ErrorType       string // The error type for serialization decisions
	ValidatorID     string
	FieldName       string // Only set for field-scope errors
	LineNumber      int    // For per-record attribution in group validators
	RecordType      string // For per-record attribution in group validators
	Error           error  // Set if expression evaluation failed
	DataFileContext *DataFileContext
	Validator       *CompiledValidator
}

// BlocksRecord returns true if this error type blocks record serialization.
func (vr *ValidationResult) BlocksRecord() bool {
	return vr.ErrorType == ErrorTypeRecordPreCheck || vr.ErrorType == ErrorTypePreCheck
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

	// Get buffer from pool
	buf := bufPool.Get().(*bytes.Buffer)
	buf.Reset()

	if err := vr.Validator.Message.Execute(buf, ctx); err != nil {
		bufPool.Put(buf)
		return vr.ValidatorID + ": template error: " + err.Error()
	}

	// Copy result and return buffer to pool
	result := buf.String()
	bufPool.Put(buf)
	return result
}

// RecordValidationResult contains all validation results for a single record.
type RecordValidationResult struct {
	Record       *parser.ParsedRecord
	RecordErrors []*ValidationResult // All record-scope errors
	FieldErrors  []*ValidationResult // All field-scope errors
	Skipped      bool                // True if field/record validators were skipped due to blocking errors
}

// HasErrors returns true if this record has any validation errors.
func (rvr *RecordValidationResult) HasErrors() bool {
	return len(rvr.RecordErrors) > 0 || len(rvr.FieldErrors) > 0
}

// HasBlockingErrors returns true if this record has errors that block serialization.
// This checks for RECORD_PRE_CHECK errors.
func (rvr *RecordValidationResult) HasBlockingErrors() bool {
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

// AllErrors returns all errors from all scopes.
func (rvr *RecordValidationResult) AllErrors() []*ValidationResult {
	total := len(rvr.RecordErrors) + len(rvr.FieldErrors)
	if total == 0 {
		return nil
	}
	result := make([]*ValidationResult, 0, total)
	result = append(result, rvr.RecordErrors...)
	result = append(result, rvr.FieldErrors...)
	return result
}

// GroupValidationResult contains all validation results for a group (case).
type GroupValidationResult struct {
	Group         *parser.ParsedGroup
	GroupErrors   []*ValidationResult // All group-scope errors
	RecordResults []*RecordValidationResult
}

// HasErrors returns true if this group has any validation errors.
func (gvr *GroupValidationResult) HasErrors() bool {
	if len(gvr.GroupErrors) > 0 {
		return true
	}
	for _, rr := range gvr.RecordResults {
		if rr.HasErrors() {
			return true
		}
	}
	return false
}

// HasBlockingGroupErrors returns true if this group has errors that block serialization.
// This checks for CASE_CONSISTENCY errors at the group level and per-record level.
// A CASE_CONSISTENCY error means "this case/group has a consistency problem" and should
// block serialization regardless of whether the error is on the group or an individual record.
func (gvr *GroupValidationResult) HasBlockingGroupErrors() bool {
	for _, err := range gvr.GroupErrors {
		if err.BlocksGroup() {
			return true
		}
	}
	for _, rr := range gvr.RecordResults {
		for _, err := range rr.RecordErrors {
			if err.BlocksGroup() {
				return true
			}
		}
		for _, err := range rr.FieldErrors {
			if err.BlocksGroup() {
				return true
			}
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

// AllGroupErrors returns all group-level errors.
func (gvr *GroupValidationResult) AllGroupErrors() []*ValidationResult {
	if len(gvr.GroupErrors) == 0 {
		return nil
	}
	return gvr.GroupErrors
}

// TotalErrorCount returns the total number of errors across all scopes.
func (gvr *GroupValidationResult) TotalErrorCount() int {
	count := len(gvr.GroupErrors)
	for _, rr := range gvr.RecordResults {
		count += len(rr.RecordErrors) + len(rr.FieldErrors)
	}
	return count
}

// AddRecordError adds an error attributed to a specific record from a group-scope validator.
// This is used for per_record result mode group validators.
func (gvr *GroupValidationResult) AddRecordError(rec *parser.ParsedRecord, validator *CompiledValidator, err error) {
	// Find the matching RecordValidationResult
	for _, rr := range gvr.RecordResults {
		if rr.Record.GetLineNumber() == rec.GetLineNumber() {
			vr := &ValidationResult{
				Valid:       false,
				ErrorType:   validator.ErrorType,
				ValidatorID: validator.ID,
				LineNumber:  rec.GetLineNumber(),
				RecordType:  rec.GetRecordType(),
				Error:       err,
				Validator:   validator,
			}
			rr.RecordErrors = append(rr.RecordErrors, vr)
			return
		}
	}
}

// AppendResultToRecordErrors routes a ValidationResult to the correct record
// by matching on LineNumber. Used by ExecuteGroup for per_record results.
func (gvr *GroupValidationResult) AppendResultToRecordErrors(vr *ValidationResult) {
	for _, rr := range gvr.RecordResults {
		if rr.Record.GetLineNumber() == vr.LineNumber {
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
	ID          string
	Scope       string             // "field", "record", or "group"
	ErrorType   string             // The declared error type (or default based on scope)
	ResultMode  string             // "single" (default) or "per_record" (for group validators)
	Expr        *CompiledExpr      // Pointer to shared compiled expr
	Message     *template.Template // Pre-resolved (default or override)
	Fields      []string           // Fields involved (for record/group validators)
	Params      map[string]any     // Runtime params for expressions (e.g., {n: 9})
	Description string             // Human-readable description for documentation generation
}
