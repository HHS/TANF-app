package parser

import (
	"fmt"
	"strconv"
	"strings"

	"go-parser/internal/decoder"
	"go-parser/internal/filespec"
	"go-parser/internal/schema"
)

// FieldExtractor extracts field values from rows based on the file format.
type FieldExtractor interface {
	Extract(row decoder.Row, field *schema.FieldDef) (any, error)
}

// GetExtractor returns the appropriate extractor for the given format.
func GetExtractor(format filespec.Format) FieldExtractor {
	switch format {
	case filespec.FormatPositional:
		return &PositionalExtractor{}
	case filespec.FormatColumnar:
		return &ColumnarExtractor{}
	default:
		panic(fmt.Sprintf("unknown format: %s", format))
	}
}

// PositionalExtractor extracts fields from positional (fixed-width) rows.
type PositionalExtractor struct{}

func (e *PositionalExtractor) Extract(row decoder.Row, field *schema.FieldDef) (any, error) {
	// Type assert to PositionalRow
	pr, ok := row.(*decoder.PositionalRow)
	if !ok {
		return nil, fmt.Errorf("expected PositionalRow, got %T", row)
	}

	// Extract raw string value using byte positions
	rawValue := pr.Slice(field.Start, field.End)

	// Apply transformation if specified
	if field.Transform != "" {
		rawValue = applyTransform(rawValue, field.Transform)
	}

	// Convert to appropriate type
	return convertValue(rawValue, field.Type)
}

// ColumnarExtractor extracts fields from columnar (CSV/XLSX) rows.
type ColumnarExtractor struct{}

func (e *ColumnarExtractor) Extract(row decoder.Row, field *schema.FieldDef) (any, error) {
	// Type assert to ColumnarRow
	cr, ok := row.(*decoder.ColumnarRow)
	if !ok {
		return nil, fmt.Errorf("expected ColumnarRow, got %T", row)
	}

	// Extract value using column index
	val := cr.Column(field.Column)
	if val == nil {
		return nil, nil // Column doesn't exist
	}

	// Apply transformation if specified
	if field.Transform != "" {
		// Convert to string first for transformation
		strVal := fmt.Sprintf("%v", val)
		strVal = applyTransform(strVal, field.Transform)
		return convertValue(strVal, field.Type)
	}

	// Handle type conversion
	// XLSX may return typed values, CSV returns strings
	switch v := val.(type) {
	case string:
		return convertValue(v, field.Type)
	case int, int64, float64:
		// Already numeric - return as-is if type matches
		if field.Type == "int" {
			return toInt(v), nil
		}
		return fmt.Sprintf("%v", v), nil
	default:
		return convertValue(fmt.Sprintf("%v", v), field.Type)
	}
}

// convertValue converts a string value to the appropriate Go type.
func convertValue(rawValue, fieldType string) (any, error) {
	// Check for empty value
	trimmed := strings.TrimSpace(rawValue)
	if trimmed == "" {
		return nil, nil
	}

	switch fieldType {
	case "int":
		i, err := strconv.Atoi(trimmed)
		if err != nil {
			return nil, fmt.Errorf("cannot convert %q to int: %w", rawValue, err)
		}
		return i, nil

	case "string":
		return rawValue, nil // Don't trim - preserve exact value

	default:
		return nil, fmt.Errorf("unknown field type: %s", fieldType)
	}
}

// toInt converts various numeric types to int.
func toInt(v any) int {
	switch n := v.(type) {
	case int:
		return n
	case int64:
		return int(n)
	case float64:
		return int(n)
	default:
		return 0
	}
}

// Transform function registry
var transforms = map[string]func(string) string{
	"zero_pad_3": func(s string) string {
		trimmed := strings.TrimSpace(s)
		if len(trimmed) < 3 {
			return fmt.Sprintf("%03s", trimmed)
		}
		return trimmed
	},
	"zero_pad_5": func(s string) string {
		trimmed := strings.TrimSpace(s)
		if len(trimmed) < 5 {
			return fmt.Sprintf("%05s", trimmed)
		}
		return trimmed
	},
	// Add more transforms as needed
}

func applyTransform(value, transformName string) string {
	if fn, ok := transforms[transformName]; ok {
		return fn(value)
	}
	return value // Unknown transform - return unchanged
}
