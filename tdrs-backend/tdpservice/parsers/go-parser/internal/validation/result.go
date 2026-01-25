package validation

import (
	"bytes"
	"text/template"
)

// ValidationResult represents the outcome of a single validator execution.
type ValidationResult struct {
	Valid       bool
	Category    int
	ValidatorID string
	FieldName   string // Only set for Cat2 errors
	Error       error  // Set if expression evaluation failed
	Validator   *CompiledValidator
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
	Record     Record
	Cat1Errors []*ValidationResult
	Cat2Errors []*ValidationResult
	Cat3Errors []*ValidationResult
	Skipped    bool // True if Cat2/Cat3 were skipped due to Cat1/Cat4 failure
}

// HasErrors returns true if this record has any validation errors.
func (rvr *RecordValidationResult) HasErrors() bool {
	return len(rvr.Cat1Errors) > 0 || len(rvr.Cat2Errors) > 0 || len(rvr.Cat3Errors) > 0
}

// HasCat1Errors returns true if this record has category 1 errors.
// Records with Cat1 errors should not be serialized to the database.
func (rvr *RecordValidationResult) HasCat1Errors() bool {
	return len(rvr.Cat1Errors) > 0
}

// ShouldSerialize returns true if this record should be written to the database.
// Records with Cat1 errors are rejected and should not be serialized.
func (rvr *RecordValidationResult) ShouldSerialize() bool {
	return !rvr.HasCat1Errors()
}

// AllErrors returns all errors from all categories.
func (rvr *RecordValidationResult) AllErrors() []*ValidationResult {
	total := len(rvr.Cat1Errors) + len(rvr.Cat2Errors) + len(rvr.Cat3Errors)
	if total == 0 {
		return nil
	}
	result := make([]*ValidationResult, 0, total)
	result = append(result, rvr.Cat1Errors...)
	result = append(result, rvr.Cat2Errors...)
	result = append(result, rvr.Cat3Errors...)
	return result
}

// GroupValidationResult contains all validation results for a group (case).
type GroupValidationResult struct {
	Group         WrappedGroup
	Cat4Errors    []*ValidationResult
	RecordResults []*RecordValidationResult
}

// HasErrors returns true if this group has any validation errors.
func (gvr *GroupValidationResult) HasErrors() bool {
	if len(gvr.Cat4Errors) > 0 {
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
func (gvr *GroupValidationResult) HasCat4Errors() bool {
	return len(gvr.Cat4Errors) > 0
}

// ShouldSerialize returns true if this group should be written to the database.
// Groups with Cat4 errors are rejected and should not be serialized.
func (gvr *GroupValidationResult) ShouldSerialize() bool {
	return !gvr.HasCat4Errors()
}

// GetSerializableRecordResults returns only the record results that should be serialized.
// Records with Cat1 errors are filtered out.
func (gvr *GroupValidationResult) GetSerializableRecordResults() []*RecordValidationResult {
	if gvr.HasCat4Errors() {
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

// TotalErrorCount returns the total number of errors across all categories.
func (gvr *GroupValidationResult) TotalErrorCount() int {
	count := len(gvr.Cat4Errors)
	for _, rr := range gvr.RecordResults {
		count += len(rr.Cat1Errors) + len(rr.Cat2Errors) + len(rr.Cat3Errors)
	}
	return count
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
	ID       string
	Category int
	Expr     *CompiledExpr      // Pointer to shared compiled expr
	Message  *template.Template // Pre-resolved (default or override)
	Fields   []string           // Fields involved (for Cat3)
	Params   map[string]any     // Runtime params for expressions (e.g., {n: 9})
}
