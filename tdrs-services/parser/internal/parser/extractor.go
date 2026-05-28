package parser

import (
	"fmt"
	"strconv"
	"strings"

	"go-parser/internal/decoder"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
)

// FieldGetter provides access to previously extracted field values.
// This interface is satisfied by both map[string]any (wrapped) and *schema.ParsedRecord.
type FieldGetter interface {
	// GetField returns the value for a field name, or nil if not found.
	GetField(name string) any
}

// MapFieldGetter wraps a map[string]any to implement FieldGetter.
type MapFieldGetter map[string]any

// GetField implements FieldGetter for maps.
func (m MapFieldGetter) GetField(name string) any {
	return m[name]
}

// ParsedFieldCache stores ParsedField entries while implementing FieldGetter.
// This is used during parsing to cache shared fields with their FieldDef pointers.
type ParsedFieldCache map[string]ParsedField

// GetField implements FieldGetter by returning only the value.
func (c ParsedFieldCache) GetField(name string) any {
	if pf, ok := c[name]; ok {
		return pf.Value
	}
	return nil
}

// FieldExtractor extracts field values from rows based on the file format.
type FieldExtractor interface {
	// Extract extracts a field value from a row.
	// For computed fields (SourceField != ""), looks up the source value from extractedFields.
	// ctx may be nil if no runtime context is available.
	// extractedFields may be nil if no computed fields are expected.
	Extract(
		row decoder.Row,
		field *schema.FieldDef,
		ctx *ParseContext,
		extractedFields FieldGetter,
	) (any, error)
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

func (e *PositionalExtractor) Extract(
	row decoder.Row,
	field *schema.FieldDef,
	ctx *ParseContext,
	extractedFields FieldGetter,
) (any, error) {
	var rawValue string

	if field.SourceField != "" {
		// Computed field - get raw value from already-extracted field
		src := extractedFields.GetField(field.SourceField)
		if src == nil {
			return nil, fmt.Errorf("source field %s not found for computed field %s",
				field.SourceField, field.Name)
		}
		rawValue = fmt.Sprintf("%v", src)
	} else {
		// Regular field - extract from row position
		pr, ok := row.(*decoder.PositionalRow)
		if !ok {
			return nil, fmt.Errorf("expected PositionalRow, got %T", row)
		}
		rawValue = pr.Slice(field.Start, field.End)
	}

	// Apply transformation if specified
	if field.Transform != nil {
		transformed, err := ApplyTransform(
			field.Transform.Name,
			rawValue,
			field.Transform.Params,
			ctx,
		)
		if err != nil {
			return nil, fmt.Errorf("transform %s on field %s failed: %w",
				field.Transform.Name, field.Name, err)
		}
		rawValue = transformed
	}

	return convertValue(rawValue, field.Type)
}

// ColumnarExtractor extracts fields from columnar (CSV/XLSX) rows.
type ColumnarExtractor struct{}

func (e *ColumnarExtractor) Extract(
	row decoder.Row,
	field *schema.FieldDef,
	ctx *ParseContext,
	extractedFields FieldGetter,
) (any, error) {
	var rawValue string

	if field.SourceField != "" {
		// Computed field - get raw value from already-extracted field
		src := extractedFields.GetField(field.SourceField)
		if src == nil {
			return nil, fmt.Errorf("source field %s not found for computed field %s",
				field.SourceField, field.Name)
		}
		rawValue = fmt.Sprintf("%v", src)
	} else {
		// Regular field - extract from column
		cr, ok := row.(*decoder.ColumnarRow)
		if !ok {
			return nil, fmt.Errorf("expected ColumnarRow, got %T", row)
		}
		val := cr.Column(field.Column)
		if val == nil {
			return nil, nil
		}
		rawValue = fmt.Sprintf("%v", val)
	}

	// Apply transformation if specified
	if field.Transform != nil {
		transformed, err := ApplyTransform(
			field.Transform.Name,
			rawValue,
			field.Transform.Params,
			ctx,
		)
		if err != nil {
			return nil, fmt.Errorf("transform %s on field %s failed: %w",
				field.Transform.Name, field.Name, err)
		}
		rawValue = transformed
	}

	return convertValue(rawValue, field.Type)
}

// convertValue converts a string value to the appropriate Go type.
func convertValue(rawValue, fieldType string) (any, error) {
	// Check for empty value
	trimmed := strings.TrimSpace(rawValue)
	if trimmed == "" || isFillValue(rawValue, '#') || isFillValue(rawValue, '_') {
		return nil, nil
	}

	switch fieldType {
	case "integer":
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

func isFillValue(rawValue string, fill rune) bool {
	if rawValue == "" {
		return false
	}
	for _, r := range rawValue {
		if r != fill {
			return false
		}
	}
	return true
}
