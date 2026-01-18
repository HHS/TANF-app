package writer

import (
	"encoding/json"
	"time"

	"go-parser/internal/schema"
	"go-parser/internal/validation"
	valreg "go-parser/internal/validation/registry"
)

// ErrorGenerator converts ValidationResults to database error rows.
// It uses the message registry to generate human-readable error messages.
type ErrorGenerator struct {
	messageRegistry *valreg.MessageRegistry
	datafileID      int32
}

// NewErrorGenerator creates an error generator with the given message registry.
func NewErrorGenerator(messageRegistry *valreg.MessageRegistry, datafileID int32) *ErrorGenerator {
	return &ErrorGenerator{
		messageRegistry: messageRegistry,
		datafileID:      datafileID,
	}
}

// GenerateRow converts a ValidationResult to a database row for the parsers_parsererror table.
// Returns a slice of values matching the parserErrorColumns order:
// row_number, column_number, item_number, field_name, case_number, rpt_month_year,
// error_message, error_type, created_at, fields_json, content_type_id, file_id,
// object_id, deprecated, values_json
func (eg *ErrorGenerator) GenerateRow(result *validation.ValidationResult, caseNumber, rptMonthYear string) []any {
	// Get field info from schema if available
	var fieldName, itemNum, friendlyName string
	var columnNumber int

	if result.FieldName != "" {
		fieldName = result.FieldName
	}

	if result.Schema != nil && result.FieldIndex >= 0 {
		fieldDef := eg.getFieldDef(result.Schema, result.FieldIndex, result.Record)
		if fieldDef != nil {
			if fieldName == "" {
				fieldName = fieldDef.Name
			}
			itemNum = fieldDef.Item
			friendlyName = fieldDef.FriendlyName
			columnNumber = result.FieldIndex
		}
	}

	// Get row number
	var rowNumber int
	if result.Record != nil {
		rowNumber = result.Record.LineNumber
	}

	// Generate error message using template
	errorMessage := eg.generateMessage(result, friendlyName, itemNum)

	// Get error type
	errorType := eg.getErrorType(result)

	// Build fields_json from record if available
	var fieldsJSON, valuesJSON []byte
	if result.Record != nil {
		fieldsJSON, _ = eg.buildFieldsJSON(result.Record)
		valuesJSON, _ = eg.buildValuesJSON(result)
	}

	// Check deprecated flag from config
	deprecated := false
	if result.Config != nil {
		deprecated = result.Config.Deprecated
	}

	return []any{
		rowNumber,        // row_number
		columnNumber,     // column_number
		itemNum,          // item_number
		fieldName,        // field_name
		caseNumber,       // case_number
		rptMonthYear,     // rpt_month_year
		errorMessage,     // error_message
		errorType,        // error_type
		time.Now(),       // created_at
		fieldsJSON,       // fields_json
		nil,              // content_type_id (set by Django)
		eg.datafileID,    // file_id
		nil,              // object_id (set by Django)
		deprecated,       // deprecated
		valuesJSON,       // values_json
	}
}

// getFieldDef retrieves the field definition for a given field index.
func (eg *ErrorGenerator) getFieldDef(sch *schema.CompiledSchema, fieldIndex int, record *schema.ParsedRecord) *schema.FieldDef {
	if sch == nil || fieldIndex < 0 {
		return nil
	}

	// Walk through shared fields first
	sharedFields := sch.Shared
	if fieldIndex < len(sharedFields) {
		return &sharedFields[fieldIndex]
	}

	// Then check segment fields if record has a segment
	if record != nil && sch.NumSegments() > 0 {
		segIdx := record.SegmentIndex
		if segIdx >= 0 && segIdx < len(sch.Segments) {
			segFields := sch.Segments[segIdx].Fields
			adjustedIdx := fieldIndex - len(sharedFields)
			if adjustedIdx >= 0 && adjustedIdx < len(segFields) {
				return &segFields[adjustedIdx]
			}
		}
	}

	return nil
}

// generateMessage creates the error message using the message registry.
func (eg *ErrorGenerator) generateMessage(result *validation.ValidationResult, friendlyName, itemNum string) string {
	// If config has inline message override, use that
	if result.Config != nil && result.Config.Message != "" {
		tmpl, err := eg.messageRegistry.ParseInline(result.ValidatorID, result.Config.Message)
		if err == nil {
			ctx := eg.buildTemplateContext(result, friendlyName, itemNum)
			if msg, err := valreg.Execute(tmpl, ctx); err == nil && msg != "" {
				return msg
			}
		}
	}

	// Look up template from registry
	var schemaPath string
	if result.Schema != nil {
		schemaPath = result.Schema.Path
	}
	tmpl := eg.messageRegistry.GetTemplate(result.ValidatorID, schemaPath, result.FieldName)
	if tmpl == nil {
		// Fallback to a generic message
		return result.ValidatorID + " validation failed"
	}

	ctx := eg.buildTemplateContext(result, friendlyName, itemNum)
	msg, err := valreg.Execute(tmpl, ctx)
	if err != nil {
		return result.ValidatorID + " validation failed"
	}
	return msg
}

// buildTemplateContext creates the context for template execution.
func (eg *ErrorGenerator) buildTemplateContext(result *validation.ValidationResult, friendlyName, itemNum string) *valreg.TemplateContext {
	ctx := &valreg.TemplateContext{
		FriendlyName: friendlyName,
		ItemNum:      itemNum,
		FieldName:    result.FieldName,
	}

	if result.Schema != nil {
		ctx.RecordType = result.Schema.RecordType
	}

	if result.Record != nil {
		ctx.Row = result.Record.LineNumber

		// Get the actual value that failed validation
		if result.FieldIndex >= 0 && result.FieldIndex < len(result.Record.Fields) {
			ctx.Value = result.Record.Fields[result.FieldIndex]
		}
	}

	// Copy params from config
	if result.Config != nil && result.Config.Params != nil {
		ctx.Params = result.Config.Params
	}

	return ctx
}

// getErrorType determines the error type string for a validation result.
func (eg *ErrorGenerator) getErrorType(result *validation.ValidationResult) string {
	// Config-level override takes precedence
	if result.Config != nil && result.Config.ErrorType != "" {
		return result.Config.ErrorType
	}

	// Fall back to category default
	return result.Category.String()
}

// buildFieldsJSON creates a JSON representation of the record fields.
func (eg *ErrorGenerator) buildFieldsJSON(record *schema.ParsedRecord) ([]byte, error) {
	if record == nil || record.Schema == nil {
		return nil, nil
	}

	fields := make(map[string]any)
	for fieldName, idx := range record.Schema.FieldIndex {
		if idx < len(record.Fields) {
			fields[fieldName] = record.Fields[idx]
		}
	}

	return json.Marshal(fields)
}

// buildValuesJSON creates a JSON representation of relevant values for the error.
func (eg *ErrorGenerator) buildValuesJSON(result *validation.ValidationResult) ([]byte, error) {
	values := make(map[string]any)

	// Add the failed field value
	if result.Record != nil && result.FieldIndex >= 0 && result.FieldIndex < len(result.Record.Fields) {
		values["value"] = result.Record.Fields[result.FieldIndex]
	}

	// Add validator params if any
	if result.Config != nil && len(result.Config.Params) > 0 {
		values["params"] = result.Config.Params
	}

	if len(values) == 0 {
		return nil, nil
	}

	return json.Marshal(values)
}
