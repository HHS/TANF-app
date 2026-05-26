package validation

import (
	"strings"
	"text/template"

	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
	"go-parser/internal/parser"
)

var noRecordsCreatedMessage = template.Must(
	template.New("no_records_created").Parse("No records created."),
)

var fieldRequiredMessage = template.Must(
	template.New("field_required").Parse("{{.RecordType}} Item {{.Item}} ({{.FriendlyName}}): field is required but a value was not provided."),
)

// ValidationOrchestrator coordinates validation across all scopes.
// Execution order: group → record (precheck) → field → record (consistency)
// Always run group and record precheck; skip field and record consistency if blocked.
type ValidationOrchestrator struct {
	registry     *ValidatorRegistry
	shortCircuit bool
}

// FileRecordStats contains file-level parsing context for header/trailer validation.
type FileRecordStats struct {
	DetailRows         int64
	MaxLineNumber      int
	HeaderCount        int
	HeaderRowNumber    int
	HeaderValid        bool
	TrailerCount       int
	TrailerRowNumber   int
	TrailerRecordCount int
	TrailerValid       bool
}

// NewFileRecordStats seeds file-level context from the already-validated header.
func NewFileRecordStats(parseCtx *parser.ParseContext) *FileRecordStats {
	stats := &FileRecordStats{}
	if parseCtx != nil && parseCtx.Header != nil {
		stats.HeaderCount = 1
		stats.HeaderRowNumber = parseCtx.Header.LineNumber
		stats.HeaderValid = true
	}
	return stats
}

// TrailerRowValidationResult contains the validation outcome for one trailer row.
type TrailerRowValidationResult struct {
	Record           *parser.ParsedRecord
	ValidationResult *RecordValidationResult
	ParseError       error
	MultipleTrailers bool
}

// NewValidationOrchestrator creates a new validation orchestrator.
// When shortCircuit is true, field and record consistency validators are skipped
// if precheck or group validators fail (default production behavior).
func NewValidationOrchestrator(registry *ValidatorRegistry, shortCircuit bool) *ValidationOrchestrator {
	return &ValidationOrchestrator{
		registry:     registry,
		shortCircuit: shortCircuit,
	}
}

// ValidateGroup validates a single group.
// Execution order: group → record (precheck) → field → record (consistency)
// Always run group and record precheck; skip field and record consistency if blocked.
func (o *ValidationOrchestrator) ValidateGroup(group *parser.ParsedGroup, filespecKey string, dfCtx *DataFileContext) *GroupValidationResult {
	result := &GroupValidationResult{
		Group: group,
	}

	// Initialize record results for all records in the group
	// This is needed for per-record error attribution from group validators
	for _, rec := range group.Records {
		result.RecordResults = append(result.RecordResults, &RecordValidationResult{Record: rec})
	}

	// Phase 1: Group validation (always runs)
	groupEnv := NewGroupEnv(group)
	groupEnv.DataFileContext = dfCtx
	for _, validator := range o.registry.GetGroupValidators(filespecKey) {
		groupEnv.Params = validator.Params // Set params for this validator

		for _, vr := range ExecuteGroup(validator, groupEnv) {
			vr.DataFileContext = dfCtx
			vr.ErrorType = validator.ErrorType
			if validator.ResultMode == "per_record" {
				result.AppendResultToRecordErrors(vr)
			} else {
				result.GroupErrors = append(result.GroupErrors, vr)
			}
		}
	}

	// Check if blocked by group-level errors
	groupBlocked := result.HasBlockingGroupErrors()

	// Phase 2: Validate each record
	for i, rec := range group.Records {
		o.validateRecord(result.RecordResults[i], rec, groupBlocked, dfCtx)
	}

	return result
}

// CreateNoRecordsCreatedError builds a synthetic validation result for the
// pipeline case where processing completes without writing any records.
func (o *ValidationOrchestrator) CreateNoRecordsCreatedError() *ValidationResult {
	return &ValidationResult{
		Valid:       false,
		ErrorType:   ErrorTypePreCheck,
		ValidatorID: "no_records_created",
		LineNumber:  0,
		Validator: &CompiledValidator{
			ID:         "no_records_created",
			Scope:      ScopeGroup,
			ErrorType:  ErrorTypePreCheck,
			ResultMode: "single",
			Message:    noRecordsCreatedMessage,
		},
	}
}

// IsValidZeroRecordSubmission returns whether file-level context describes
// a structurally valid zero-record submission for a section that allows it.
func (o *ValidationOrchestrator) IsValidZeroRecordSubmission(sectionName string, stats *FileRecordStats) bool {
	if stats == nil {
		return false
	}
	switch sectionName {
	case "Active Case Data", "Closed Case Data", "Aggregate Data", "Stratum Data":
	default:
		return false
	}
	return stats.DetailRows == 0 &&
		stats.HeaderCount == 1 &&
		stats.HeaderValid &&
		stats.TrailerCount == 1 &&
		stats.TrailerValid &&
		stats.TrailerRecordCount == 0
}

// ValidateTrailerRow parses and validates a trailer row, updating file-level
// trailer context while leaving error serialization to the pipeline.
func (o *ValidationOrchestrator) ValidateTrailerRow(
	row decoder.Row,
	trailerSchema *schema.CompiledSchema,
	dfCtx *DataFileContext,
	stats *FileRecordStats,
) *TrailerRowValidationResult {
	result := &TrailerRowValidationResult{}
	if stats == nil {
		stats = &FileRecordStats{}
	}

	stats.TrailerCount++
	result.MultipleTrailers = stats.TrailerCount > 1
	if trailerSchema == nil {
		return result
	}

	trailerRecord, err := parser.ParseTrailer(row, trailerSchema)
	if err != nil {
		result.ParseError = err
		return result
	}

	recordResult := o.ValidateRecord(trailerRecord, dfCtx)
	result.Record = trailerRecord
	result.ValidationResult = recordResult

	if stats.TrailerCount == 1 {
		stats.TrailerRowNumber = row.LineNum()
		stats.TrailerRecordCount = trailerRecord.GetInt("record_count")
		stats.TrailerValid = !recordResult.HasErrors()
	}
	return result
}

// ValidateRecord validates a single record.
func (o *ValidationOrchestrator) ValidateRecord(rec *parser.ParsedRecord, dfCtx *DataFileContext) *RecordValidationResult {
	result := &RecordValidationResult{Record: rec}
	o.validateRecord(result, rec, false, dfCtx)
	return result
}

// ValidateHeader validates a single header record with DataFileContext injected
// into the validation environments. This runs the same phases as validateRecord
// (record precheck → field → record consistency) but with DataFileContext available
// to expressions for cross-validation against submission metadata.
func (o *ValidationOrchestrator) ValidateHeader(headerRec *parser.ParsedRecord, dfCtx *DataFileContext) *RecordValidationResult {
	result := &RecordValidationResult{Record: headerRec}
	schemaKey := validationSchemaKey(headerRec)
	recordEnv := NewRecordEnv(headerRec)
	recordEnv.DataFileContext = dfCtx

	// Phase 1: Run PRE_CHECK and RECORD_PRE_CHECK validators
	recordBlocked := false
	for _, validator := range o.registry.GetRecordValidators(schemaKey) {
		if validator.ErrorType != ErrorTypeRecordPreCheck && validator.ErrorType != ErrorTypePreCheck {
			continue
		}
		recordEnv.Params = validator.Params
		if vr := Execute(validator, recordEnv); !vr.Valid {
			vr.DataFileContext = dfCtx
			vr.ErrorType = validator.ErrorType
			result.RecordErrors = append(result.RecordErrors, vr)
			recordBlocked = true
		}
	}

	if o.shortCircuit && recordBlocked {
		result.Skipped = true
		return result
	}

	// Phase 2: Field validation
	fieldEnv := &FieldEnv{DataFileContext: dfCtx}
	for fieldName, validators := range o.registry.GetFieldValidatorsForRecord(schemaKey) {
		value := headerRec.Get(fieldName)
		required := headerRec.IsFieldRequired(fieldName)

		if !required {
			continue
		}

		if fieldValueIsEmpty(value) {
			result.FieldErrors = append(result.FieldErrors, &ValidationResult{
				Valid:       false,
				ValidatorID: "field_required",
				ErrorType:   ErrorTypeFieldValue,
				FieldName:   fieldName,
				Validator: &CompiledValidator{
					ID:         "field_required",
					Scope:      ScopeField,
					ErrorType:  ErrorTypeFieldValue,
					ResultMode: "single",
					Message:    fieldRequiredMessage,
				},
			})
			continue
		}

		fieldEnv.Value = value
		for _, cv := range validators {
			fieldEnv.Params = cv.Params
			if vr := Execute(cv, fieldEnv); !vr.Valid {
				vr.DataFileContext = dfCtx
				vr.ErrorType = cv.ErrorType
				vr.FieldName = fieldName
				result.FieldErrors = append(result.FieldErrors, vr)
			}
		}
	}

	// Phase 3: Non-precheck record validators (consistency checks)
	for _, cv := range o.registry.GetRecordValidators(schemaKey) {
		if cv.ErrorType == ErrorTypeRecordPreCheck || cv.ErrorType == ErrorTypePreCheck {
			continue
		}
		recordEnv.Params = cv.Params
		if vr := Execute(cv, recordEnv); !vr.Valid {
			vr.DataFileContext = dfCtx
			vr.ErrorType = cv.ErrorType
			result.RecordErrors = append(result.RecordErrors, vr)
		}
	}

	return result
}

// validateRecord validates a single record, updating the provided result.
// Called internally by ValidateGroup.
func (o *ValidationOrchestrator) validateRecord(result *RecordValidationResult, rec *parser.ParsedRecord, groupBlocked bool, dfCtx *DataFileContext) {
	schemaKey := validationSchemaKey(rec)
	recordEnv := NewRecordEnv(rec)
	recordEnv.DataFileContext = dfCtx

	// Phase 1: Run RECORD_PRE_CHECK and PRE_CHECK validators (always runs, can block)
	for _, cv := range o.registry.GetRecordValidators(schemaKey) {
		// Skip non-precheck validators in this phase
		if cv.ErrorType == ErrorTypeRecordPreCheck || cv.ErrorType == ErrorTypePreCheck {
			recordEnv.Params = cv.Params
			if vr := Execute(cv, recordEnv); !vr.Valid {
				vr.DataFileContext = dfCtx
				vr.ErrorType = cv.ErrorType
				result.RecordErrors = append(result.RecordErrors, vr)
			}
		}
	}

	// Check if blocked by record-level errors
	recordBlocked := result.HasBlockingErrors()

	// Short-circuit: skip field and non-precheck record validators if group or record is blocked
	if o.shortCircuit && (groupBlocked || recordBlocked) {
		result.Skipped = true
		return
	}

	// Phase 2: Field validation
	fieldEnv := &FieldEnv{DataFileContext: dfCtx} // Reuse env for efficiency
	for fieldName, validators := range o.registry.GetFieldValidatorsForRecord(schemaKey) {
		value := rec.Get(fieldName)
		required := rec.IsFieldRequired(fieldName)

		if !required {
			continue
		}

		if fieldValueIsEmpty(value) {
			result.FieldErrors = append(result.FieldErrors, &ValidationResult{
				Valid:       false,
				ValidatorID: "field_required",
				ErrorType:   ErrorTypeFieldValue,
				FieldName:   fieldName,
				Validator: &CompiledValidator{
					ID:         "field_required",
					Scope:      ScopeField,
					ErrorType:  ErrorTypeFieldValue,
					ResultMode: "single",
					Message:    fieldRequiredMessage,
				},
			})
			continue
		}

		fieldEnv.Value = value
		for _, cv := range validators {
			fieldEnv.Params = cv.Params
			if vr := Execute(cv, fieldEnv); !vr.Valid {
				vr.DataFileContext = dfCtx
				vr.ErrorType = cv.ErrorType
				vr.FieldName = fieldName
				result.FieldErrors = append(result.FieldErrors, vr)
			}
		}
	}

	// Phase 3: Non-precheck record validators (consistency checks)
	for _, cv := range o.registry.GetRecordValidators(schemaKey) {
		if cv.ErrorType == ErrorTypeRecordPreCheck || cv.ErrorType == ErrorTypePreCheck {
			continue // Already ran in phase 1
		}
		recordEnv.Params = cv.Params
		if vr := Execute(cv, recordEnv); !vr.Valid {
			vr.DataFileContext = dfCtx
			vr.ErrorType = cv.ErrorType
			result.RecordErrors = append(result.RecordErrors, vr)
		}
	}
}

func validationSchemaKey(rec *parser.ParsedRecord) string {
	if rec.Schema != nil && rec.Schema.Path != "" {
		return rec.Schema.Path
	}
	return rec.GetRecordType()
}

func fieldValueIsEmpty(value any) bool {
	if value == nil {
		return true
	}
	if s, ok := value.(string); ok {
		return strings.TrimSpace(s) == ""
	}
	return false
}
