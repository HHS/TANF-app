// Package errors provides error generation for validation failures.
package errors

import (
	"encoding/json"
	"fmt"
	"text/template"
	"time"

	"go-parser/internal/parser"
	"go-parser/internal/schema"
	"go-parser/internal/validation"
	"go-parser/internal/validation/registry"
)

// ErrorGenerator creates ParserError rows from ValidationResults.
// It uses lazy evaluation - errors are generated at write time, not during validation.
type ErrorGenerator struct {
	messages      *registry.MessageRegistry
	categories    map[int]validation.CategoryConfig
	cachedInline  map[string]*template.Template // Cache for inline message templates
	datafileID    int32
	contentTypeID *int32 // Set by the caller if needed
}

// NewErrorGenerator creates a new error generator.
func NewErrorGenerator(messages *registry.MessageRegistry, config *validation.OrchestratorConfig) *ErrorGenerator {
	g := &ErrorGenerator{
		messages:     messages,
		categories:   make(map[int]validation.CategoryConfig),
		cachedInline: make(map[string]*template.Template),
	}

	if config != nil {
		for _, cat := range config.Categories {
			g.categories[cat.ID] = cat
		}
	}

	return g
}

// SetDatafileID sets the datafile ID for all generated errors.
func (g *ErrorGenerator) SetDatafileID(id int32) {
	g.datafileID = id
}

// SetContentTypeID sets the content type ID for all generated errors.
func (g *ErrorGenerator) SetContentTypeID(id int32) {
	g.contentTypeID = &id
}

// ParserError represents a row in the parser_error table.
// TODO: I doubt we need this struct. I think we can just use the the db package version and a converter
type ParserError struct {
	RowNumber     int
	ColumnNumber  string
	ItemNumber    string
	FieldName     string
	CaseNumber    string
	RptMonthYear  int
	ErrorMessage  string
	ErrorType     string
	CreatedAt     time.Time
	FieldsJSON    string
	ContentTypeID *int32
	FileID        int32
	ObjectID      *int32
	Deprecated    bool
	ValuesJSON    string
}

// Generate creates a ParserError from a ValidationResult.
// This is called at WRITE time for lazy error generation.
func (g *ErrorGenerator) Generate(result *validation.ValidationResult) *ParserError {
	if result == nil || result.Valid {
		return nil
	}

	// Build template context
	ctx := g.buildTemplateContext(result)

	// Resolve message template
	tmpl := g.resolveTemplate(result)

	// Execute template to generate message
	message := registry.ExecuteString(tmpl, ctx)
	if message == "" {
		// Fallback message if template execution fails
		message = fmt.Sprintf("Validation failed: %s", result.ValidatorID)
	}

	// Resolve error type
	errorType := g.resolveErrorType(result)

	// Build fields and values JSON
	fieldsJSON := g.buildFieldsJSON(result)
	valuesJSON := g.buildValuesJSON(result, ctx)

	// Extract record info
	rowNumber := 0
	caseNumber := ""
	rptMonthYear := 0

	if result.Record != nil {
		rowNumber = result.Record.LineNumber
		caseNumber = result.Record.GetString("CASE_NUMBER")
		rptMonthYear = result.Record.GetInt("RPT_MONTH_YEAR")
	} else if result.Row != nil {
		rowNumber = result.Row.LineNum()
	} else if result.Group != nil {
		caseNumber = result.Group.CaseNumber
		if len(result.Group.Records) > 0 {
			rowNumber = result.Group.Records[0].LineNumber
			rptMonthYear = result.Group.Records[0].GetInt("RPT_MONTH_YEAR")
		}
	}

	// Get field info
	itemNumber := ""
	columnNumber := ""
	fieldName := result.FieldName

	if result.Schema != nil && result.FieldIndex >= 0 {
		fieldDef := getFieldDef(result.Schema, result.FieldIndex, result.Record)
		if fieldDef != nil {
			itemNumber = fieldDef.Item
			columnNumber = fieldDef.Item
			if fieldName == "" {
				fieldName = fieldDef.Name
			}
		}
	}

	deprecated := false
	if result.Config != nil && result.Config.Deprecated {
		deprecated = true
	}

	return &ParserError{
		RowNumber:     rowNumber,
		ColumnNumber:  columnNumber,
		ItemNumber:    itemNumber,
		FieldName:     fieldName,
		CaseNumber:    caseNumber,
		RptMonthYear:  rptMonthYear,
		ErrorMessage:  truncate(message, 512),
		ErrorType:     errorType,
		CreatedAt:     time.Now(),
		FieldsJSON:    fieldsJSON,
		ContentTypeID: g.contentTypeID,
		FileID:        g.datafileID,
		ObjectID:      nil,
		Deprecated:    deprecated,
		ValuesJSON:    valuesJSON,
	}
}

// GenerateRow returns a slice of values ready for table writer insertion.
// Column order matches the parser_error table.
func (g *ErrorGenerator) GenerateRow(result *validation.ValidationResult) []any {
	err := g.Generate(result)
	if err == nil {
		return nil
	}

	return []any{
		err.RowNumber,
		err.ColumnNumber,
		err.ItemNumber,
		err.FieldName,
		err.CaseNumber,
		err.RptMonthYear,
		err.ErrorMessage,
		err.ErrorType,
		err.CreatedAt,
		err.FieldsJSON,
		err.ContentTypeID,
		err.FileID,
		err.ObjectID,
		err.Deprecated,
		err.ValuesJSON,
	}
}

// GenerateBatch generates errors for multiple results.
func (g *ErrorGenerator) GenerateBatch(results []*validation.ValidationResult) []*ParserError {
	errors := make([]*ParserError, 0, len(results))
	for _, result := range results {
		if err := g.Generate(result); err != nil {
			errors = append(errors, err)
		}
	}
	return errors
}

// buildTemplateContext creates a TemplateContext from a ValidationResult.
func (g *ErrorGenerator) buildTemplateContext(result *validation.ValidationResult) *registry.TemplateContext {
	ctx := &registry.TemplateContext{
		Row:    0,
		Extra:  make(map[string]any),
	}

	// Record type
	if result.Schema != nil {
		ctx.RecordType = result.Schema.RecordType
	}

	// Field info
	if result.Schema != nil && result.FieldIndex >= 0 {
		fieldDef := getFieldDef(result.Schema, result.FieldIndex, result.Record)
		if fieldDef != nil {
			ctx.ItemNum = fieldDef.Item
			ctx.FriendlyName = fieldDef.FriendlyName
			ctx.FieldName = fieldDef.Name
		}
	}
	if result.FieldName != "" && ctx.FieldName == "" {
		ctx.FieldName = result.FieldName
	}

	// Value
	if result.Record != nil && result.FieldIndex >= 0 && result.FieldIndex < len(result.Record.Fields) {
		ctx.Value = result.Record.Fields[result.FieldIndex]
	}

	// Row number
	if result.Record != nil {
		ctx.Row = result.Record.LineNumber
	} else if result.Row != nil {
		ctx.Row = result.Row.LineNum()
	}

	// Params from config
	if result.Config != nil && result.Config.Params != nil {
		ctx.Params = result.Config.Params
	}

	return ctx
}

// resolveTemplate finds the appropriate message template for a result.
// Priority: config.Message > field override > schema override > default
func (g *ErrorGenerator) resolveTemplate(result *validation.ValidationResult) *template.Template {
	// 1. Check for inline message in config
	if result.Config != nil && result.Config.Message != "" {
		return g.getOrParseInline(result.Config.ID, result.Config.Message)
	}

	// 2. Use registry to find best match
	schemaPath := ""
	if result.Schema != nil {
		schemaPath = result.Schema.Path
	}

	return g.messages.GetTemplate(result.ValidatorID, schemaPath, result.FieldName)
}

// getOrParseInline gets or parses an inline template.
func (g *ErrorGenerator) getOrParseInline(id, message string) *template.Template {
	key := id + ":" + message
	if t, ok := g.cachedInline[key]; ok {
		return t
	}
	t, err := g.messages.ParseInline(id, message)
	if err != nil {
		return nil
	}
	g.cachedInline[key] = t
	return t
}

// resolveErrorType determines the error type for a result.
func (g *ErrorGenerator) resolveErrorType(result *validation.ValidationResult) string {
	// 1. Check for override in config
	if result.Config != nil && result.Config.ErrorType != "" {
		return result.Config.ErrorType
	}

	// 2. Use category default
	if cat, ok := g.categories[int(result.Category)]; ok {
		return cat.DefaultErrorType
	}

	// 3. Fall back to category string
	return result.Category.String()
}

// buildFieldsJSON creates the fields_json value.
func (g *ErrorGenerator) buildFieldsJSON(result *validation.ValidationResult) string {
	fields := make(map[string]any)

	if result.FieldName != "" {
		fields["name"] = result.FieldName
	}

	if result.Schema != nil && result.FieldIndex >= 0 {
		fieldDef := getFieldDef(result.Schema, result.FieldIndex, result.Record)
		if fieldDef != nil {
			fields["item"] = fieldDef.Item
			fields["friendly_name"] = fieldDef.FriendlyName
		}
	}

	if len(fields) == 0 {
		return "{}"
	}

	data, err := json.Marshal(fields)
	if err != nil {
		return "{}"
	}
	return string(data)
}

// buildValuesJSON creates the values_json value.
func (g *ErrorGenerator) buildValuesJSON(result *validation.ValidationResult, ctx *registry.TemplateContext) string {
	values := make(map[string]any)

	if ctx.Value != nil {
		values["value"] = ctx.Value
	}

	if result.Config != nil && result.Config.Params != nil {
		for k, v := range result.Config.Params {
			values[k] = v
		}
	}

	if len(values) == 0 {
		return "{}"
	}

	data, err := json.Marshal(values)
	if err != nil {
		return "{}"
	}
	return string(data)
}

// getFieldDef gets the field definition for a field index.
func getFieldDef(cs *schema.CompiledSchema, fieldIndex int, record *parser.ParsedRecord) *schema.FieldDef {
	if cs == nil || fieldIndex < 0 {
		return nil
	}

	// Walk through shared fields first
	sharedFields := cs.Shared
	if fieldIndex < len(sharedFields) {
		return &sharedFields[fieldIndex]
	}

	// Then check segment fields if record has a segment
	if record != nil && cs.NumSegments() > 0 {
		segIdx := record.SegmentIndex
		if segIdx >= 0 && segIdx < len(cs.Segments) {
			segFields := cs.Segments[segIdx].Fields
			adjustedIdx := fieldIndex - len(sharedFields)
			if adjustedIdx >= 0 && adjustedIdx < len(segFields) {
				return &segFields[adjustedIdx]
			}
		}
	}

	return nil
}

// truncate truncates a string to maxLen characters.
func truncate(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen-3] + "..."
}
