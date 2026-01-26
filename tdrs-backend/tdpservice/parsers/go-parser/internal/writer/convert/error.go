package convert

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

// ConvertError converts a ValidationResult to a database row immediately.
// Must be called BEFORE the record is released to pool.
// Returns []any row matching parserErrorColumns order:
// row_number, column_number, item_number, field_name, case_number, rpt_month_year,
// error_message, error_type, created_at, fields_json, content_type_id, file_id,
// object_id, deprecated, values_json
func ConvertError(
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
	row := []any{
		toRowNumber(record),                          // row_number
		pgtype.Text{Valid: false},                    // column_number (not used)
		toItemNumber(vr, record),                     // item_number
		toFieldName(vr),                              // field_name
		toCaseNumber(record),                         // case_number
		toRptMonthYear(record),                       // rpt_month_year
		pgtype.Text{String: msg, Valid: msg != ""},   // error_message
		errorType,                                    // error_type
		pgtype.Timestamptz{Time: time.Now(), Valid: true}, // created_at
		fieldsJSON,                       // fields_json
		toContentTypeID(contentTypeID),   // content_type_id
		pgtype.Int4{Int32: datafileID, Valid: true}, // file_id
		toObjectID(recordUUID),           // object_id
		false,                            // deprecated
		valuesJSON,                       // values_json
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
	ctx := map[string]any{
		"RecordType": record.Schema.RecordType,
		"LineNumber": record.LineNumber,
	}

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

	// Add all validator-involved fields
	if len(vr.Validator.Fields) > 0 {
		ctx["Fields"] = vr.Validator.Fields
	}

	return vr.Message(ctx)
}

// buildFieldsJSON builds the fields_json structure from schema metadata
func buildFieldsJSON(vr *validation.ValidationResult, record *parser.ParsedRecord) []byte {
	fieldsJSON := FieldsJSON{
		FriendlyName: make(map[string]string),
		ItemNumbers:  make(map[string]string),
	}

	// Get fields involved in this validation
	fieldNames := getInvolvedFieldNames(vr, record)

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
	valuesMap := make(map[string]any)

	// Get fields involved in this validation
	fieldNames := getInvolvedFieldNames(vr, record)

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
func getInvolvedFieldNames(vr *validation.ValidationResult, record *parser.ParsedRecord) []string {
	var fieldNames []string

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

// Helper functions for building row values

func toRowNumber(record *parser.ParsedRecord) pgtype.Int4 {
	if record == nil {
		return pgtype.Int4{Valid: false}
	}
	return pgtype.Int4{Int32: int32(record.LineNumber), Valid: true}
}

func toItemNumber(vr *validation.ValidationResult, record *parser.ParsedRecord) pgtype.Text {
	if vr.FieldName != "" {
		fd := getFieldDef(record, vr.FieldName)
		if fd != nil && fd.Item != "" {
			return pgtype.Text{String: fd.Item, Valid: true}
		}
	}
	return pgtype.Text{Valid: false}
}

func toFieldName(vr *validation.ValidationResult) pgtype.Text {
	if vr.FieldName != "" {
		return pgtype.Text{String: vr.FieldName, Valid: true}
	}
	return pgtype.Text{Valid: false}
}

func toCaseNumber(record *parser.ParsedRecord) pgtype.Text {
	if record == nil {
		return pgtype.Text{Valid: false}
	}
	caseNum := record.GetString("CASE_NUMBER")
	if caseNum == "" {
		return pgtype.Text{Valid: false}
	}
	return pgtype.Text{String: caseNum, Valid: true}
}

func toRptMonthYear(record *parser.ParsedRecord) pgtype.Int4 {
	if record == nil {
		return pgtype.Int4{Valid: false}
	}
	rmy := record.GetInt("RPT_MONTH_YEAR")
	if rmy == 0 {
		return pgtype.Int4{Valid: false}
	}
	return pgtype.Int4{Int32: int32(rmy), Valid: true}
}

func toContentTypeID(contentTypeID *int32) pgtype.Int4 {
	if contentTypeID == nil {
		return pgtype.Int4{Valid: false}
	}
	return pgtype.Int4{Int32: *contentTypeID, Valid: true}
}

func toObjectID(recordUUID *pgtype.UUID) pgtype.UUID {
	if recordUUID == nil {
		return pgtype.UUID{Valid: false}
	}
	return *recordUUID
}
