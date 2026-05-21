package writer

import (
	"encoding/json"
	"time"

	"github.com/jackc/pgx/v5/pgtype"

	"go-parser/internal/config/schema"
	"go-parser/internal/parser"
	"go-parser/internal/validation"
)

// Error type mapping from Go constants to database values
// These match the Python parser's error type values
var errorTypeDBValue = map[string]string{
	validation.ErrorTypePreCheck:         "1",
	validation.ErrorTypeRecordPreCheck:   "7",
	validation.ErrorTypeFieldValue:       "2",
	validation.ErrorTypeValueConsistency: "3",
	validation.ErrorTypeCaseConsistency:  "4",
}

// FieldsJSON represents the structure for fields_json column
type FieldsJSON struct {
	FriendlyName map[string]string `json:"friendly_name"`
	ItemNumbers  map[string]string `json:"item_numbers"`
}

// SerializeError converts a ValidationResult to a database row immediately.
// Must be called BEFORE the record is released to pool.
// Returns []any row matching parserErrorColumns order:
// row_number, column_number, item_number, field_name, case_number, rpt_month_year,
// error_message, error_type, created_at, fields_json, content_type_id, file_id,
// object_id, deprecated, values_json
func SerializeError(
	vr *validation.ValidationResult,
	record *parser.ParsedRecord,
	recordUUID *pgtype.UUID,
	datafileID int32,
	contentTypeID *int32,
) []any {
	// Render message template NOW (needs record data)
	msg := renderErrorMessage(vr, record)

	// Build fields_json from schema metadata
	fieldsJSON := buildFieldsJSON(vr, record)

	// Build values_json from record field values
	valuesJSON := buildValuesJSON(vr, record)

	// Get error type for DB (mapped from Go constant)
	errorType := mapErrorType(vr.ErrorType)

	// Build row matching parserErrorColumns order
	// Use raw types where possible, nil for NULL
	row := []any{
		toErrorRowNumber(record),            // row_number (int32 or nil)
		nil,                                 // column_number (not used)
		toErrorItemNumber(vr, record),       // item_number (string or nil)
		toErrorFieldName(vr),                // field_name (string or nil)
		toErrorCaseNumber(record),           // case_number (string or nil)
		toErrorRptMonthYear(record),         // rpt_month_year (int32 or nil)
		toErrorMessage(msg),                 // error_message (string or nil)
		errorType,                           // error_type (string)
		time.Now(),                          // created_at (time.Time)
		fieldsJSON,                          // fields_json ([]byte)
		toErrorContentTypeID(contentTypeID), // content_type_id (int32 or nil)
		datafileID,                          // file_id (int32)
		toErrorObjectID(recordUUID),         // object_id (pgtype.UUID)
		false,                               // deprecated (bool)
		valuesJSON,                          // values_json ([]byte)
	}

	return row
}

// renderErrorMessage renders the validator's message template with record context.
// Called during error conversion, while record is still available.
func renderErrorMessage(vr *validation.ValidationResult, record *parser.ParsedRecord) string {
	if vr.Validator == nil || vr.Validator.Message == nil {
		return vr.ValidatorID + " validation failed"
	}

	// Build template context from record
	ctx := make(map[string]any, 10) // Pre-size for typical usage
	ctx["RecordType"] = record.Schema.RecordType
	ctx["LineNumber"] = record.LineNumber
	ctx["RecordLength"] = record.GetDecodedSize()

	// Add field-specific context if this is a field error
	if vr.FieldName != "" {
		ctx["Value"] = record.Get(vr.FieldName)
		if fd := getFieldDef(record, vr.FieldName); fd != nil {
			ctx["Item"] = fd.Item
			ctx["FriendlyName"] = fd.FriendlyName
		}
	}

	// Add validator params
	if vr.Validator.Params != nil {
		ctx["Params"] = vr.Validator.Params
	}
	if vr.DataFileContext != nil {
		ctx["DataFileContext"] = vr.DataFileContext
	}
	for key, value := range vr.Context {
		ctx[key] = value
	}

	// Add all validator-involved fields
	if len(vr.Validator.Fields) > 0 {
		ctx["Fields"] = vr.Validator.Fields

		values := make(map[string]any, len(vr.Validator.Fields))
		for _, fieldName := range vr.Validator.Fields {
			values[fieldName] = record.Get(fieldName)
		}
		ctx["Values"] = values
	}

	return vr.Message(ctx)
}

// buildFieldsJSON builds the fields_json structure from schema metadata
func buildFieldsJSON(vr *validation.ValidationResult, record *parser.ParsedRecord) []byte {
	// Get fields involved in this validation
	fieldNames := getInvolvedFieldNames(vr)

	// Pre-size maps based on expected field count
	fieldsJSON := FieldsJSON{
		FriendlyName: make(map[string]string, len(fieldNames)),
		ItemNumbers:  make(map[string]string, len(fieldNames)),
	}

	for _, fieldName := range fieldNames {
		fd := getFieldDef(record, fieldName)
		if fd != nil {
			fieldsJSON.FriendlyName[fieldName] = fd.FriendlyName
			fieldsJSON.ItemNumbers[fieldName] = fd.Item
		}
	}

	data, err := json.Marshal(fieldsJSON)
	if err != nil {
		return nil
	}
	return data
}

// buildValuesJSON builds the values_json structure from record field values
func buildValuesJSON(vr *validation.ValidationResult, record *parser.ParsedRecord) []byte {
	// Get fields involved in this validation
	fieldNames := getInvolvedFieldNames(vr)

	// Pre-size map based on expected field count
	valuesMap := make(map[string]any, len(fieldNames))

	for _, fieldName := range fieldNames {
		value := record.Get(fieldName)
		if value != nil {
			valuesMap[fieldName] = value
		}
	}

	data, err := json.Marshal(valuesMap)
	if err != nil {
		return nil
	}
	return data
}

// getInvolvedFieldNames returns the field names involved in this validation result
func getInvolvedFieldNames(vr *validation.ValidationResult) []string {
	// Pre-allocate with estimated capacity
	capacity := 1
	if vr.Validator != nil && len(vr.Validator.Fields) > 0 {
		capacity += len(vr.Validator.Fields)
	}
	fieldNames := make([]string, 0, capacity)

	// For field-scope errors, include the field name
	if vr.FieldName != "" {
		fieldNames = append(fieldNames, vr.FieldName)
	}

	// For validators with explicit fields list, include those
	if vr.Validator != nil && len(vr.Validator.Fields) > 0 {
		fieldNames = append(fieldNames, vr.Validator.Fields...)
	}

	return fieldNames
}

// getFieldDef retrieves the FieldDef for a given field name from the record's schema
func getFieldDef(record *parser.ParsedRecord, fieldName string) *schema.FieldDef {
	if record == nil || record.Schema == nil {
		return nil
	}

	// Check shared fields first
	if fd := record.Schema.GetSharedField(fieldName); fd != nil {
		return fd
	}

	// Check segment fields (use segment 0 as reference)
	return record.Schema.GetSegmentField(0, fieldName)
}

// mapErrorType maps Go error type constant to database value
func mapErrorType(errorType string) string {
	if dbVal, ok := errorTypeDBValue[errorType]; ok {
		return dbVal
	}
	// Default to VALUE_CONSISTENCY type if unknown
	return errorTypeDBValue[validation.ErrorTypeValueConsistency]
}

// Helper functions for building error row values using raw types

func toErrorRowNumber(record *parser.ParsedRecord) any {
	if record == nil {
		return nil
	}
	return int32(record.LineNumber)
}

func toErrorItemNumber(vr *validation.ValidationResult, record *parser.ParsedRecord) any {
	if vr.FieldName != "" {
		fd := getFieldDef(record, vr.FieldName)
		if fd != nil && fd.Item != "" {
			return fd.Item
		}
	}
	return nil
}

func toErrorFieldName(vr *validation.ValidationResult) any {
	if vr.FieldName != "" {
		return vr.FieldName
	}
	return nil
}

func toErrorCaseNumber(record *parser.ParsedRecord) any {
	if record == nil {
		return nil
	}
	caseNum := record.GetString("CASE_NUMBER")
	if caseNum == "" {
		return nil
	}
	return caseNum
}

func toErrorRptMonthYear(record *parser.ParsedRecord) any {
	if record == nil {
		return nil
	}
	rmy := record.GetInt("RPT_MONTH_YEAR")
	if rmy == 0 {
		return nil
	}
	return int32(rmy)
}

func toErrorMessage(msg string) any {
	if msg == "" {
		return nil
	}
	return msg
}

func toErrorContentTypeID(contentTypeID *int32) any {
	if contentTypeID == nil {
		return nil
	}
	return *contentTypeID
}

func toErrorObjectID(recordUUID *pgtype.UUID) pgtype.UUID {
	if recordUUID == nil {
		return pgtype.UUID{Valid: false}
	}
	return *recordUUID
}

// SerializeParserError creates a database error row for parser-level line errors.
func SerializeParserError(rowNumber int, message string, errorType string, datafileID int32) []any {
	return []any{
		int32(rowNumber),          // row_number
		nil,                       // column_number
		nil,                       // item_number
		nil,                       // field_name
		nil,                       // case_number
		nil,                       // rpt_month_year
		message,                   // error_message
		mapErrorType(errorType),   // error_type
		time.Now(),                // created_at
		nil,                       // fields_json
		nil,                       // content_type_id
		datafileID,                // file_id
		pgtype.UUID{Valid: false}, // object_id
		false,                     // deprecated
		nil,                       // values_json
	}
}
