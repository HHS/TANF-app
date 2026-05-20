package parser

import (
	"testing"

	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
)

func TestMapFieldGetter(t *testing.T) {
	t.Run("existing key", func(t *testing.T) {
		m := MapFieldGetter{"age": 42, "name": "Alice"}
		got := m.GetField("age")
		if got != 42 {
			t.Errorf("GetField(age) = %v, want 42", got)
		}
	})

	t.Run("missing key", func(t *testing.T) {
		m := MapFieldGetter{"age": 42}
		got := m.GetField("missing")
		if got != nil {
			t.Errorf("GetField(missing) = %v, want nil", got)
		}
	})
}

func TestParsedFieldCache(t *testing.T) {
	t.Run("existing key returns value", func(t *testing.T) {
		c := ParsedFieldCache{
			"status": {Value: "active"},
			"count":  {Value: 10},
		}
		got := c.GetField("status")
		if got != "active" {
			t.Errorf("GetField(status) = %v, want %q", got, "active")
		}
	})

	t.Run("existing key with nil value returns nil", func(t *testing.T) {
		c := ParsedFieldCache{
			"empty": {Value: nil},
		}
		got := c.GetField("empty")
		if got != nil {
			t.Errorf("GetField(empty) = %v, want nil", got)
		}
	})

	t.Run("missing key returns nil", func(t *testing.T) {
		c := ParsedFieldCache{"status": {Value: "active"}}
		got := c.GetField("missing")
		if got != nil {
			t.Errorf("GetField(missing) = %v, want nil", got)
		}
	})
}

func TestGetExtractor(t *testing.T) {
	t.Run("positional format", func(t *testing.T) {
		ext := GetExtractor(filespec.FormatPositional)
		if _, ok := ext.(*PositionalExtractor); !ok {
			t.Errorf("GetExtractor(positional) returned %T, want *PositionalExtractor", ext)
		}
	})

	t.Run("columnar format", func(t *testing.T) {
		ext := GetExtractor(filespec.FormatColumnar)
		if _, ok := ext.(*ColumnarExtractor); !ok {
			t.Errorf("GetExtractor(columnar) returned %T, want *ColumnarExtractor", ext)
		}
	})

	t.Run("unknown format panics", func(t *testing.T) {
		defer func() {
			r := recover()
			if r == nil {
				t.Fatal("GetExtractor(unknown) did not panic")
			}
			msg, ok := r.(string)
			if !ok {
				t.Fatalf("panic value is %T, want string", r)
			}
			if msg != "unknown format: bogus" {
				t.Errorf("panic message = %q, want %q", msg, "unknown format: bogus")
			}
		}()
		GetExtractor(filespec.Format("bogus"))
	})
}

func TestConvertValue(t *testing.T) {
	tests := []struct {
		name      string
		rawValue  string
		fieldType string
		want      any
		wantErr   bool
	}{
		{
			name:      "empty string returns nil",
			rawValue:  "",
			fieldType: "string",
			want:      nil,
		},
		{
			name:      "whitespace only returns nil",
			rawValue:  "   ",
			fieldType: "integer",
			want:      nil,
		},
		{
			name:      "hash fill value returns nil",
			rawValue:  "####",
			fieldType: "string",
			want:      nil,
		},
		{
			name:      "underscore fill value returns nil",
			rawValue:  "____",
			fieldType: "integer",
			want:      nil,
		},
		{
			name:      "integer success",
			rawValue:  "  42 ",
			fieldType: "integer",
			want:      42,
		},
		{
			name:      "integer negative",
			rawValue:  " -7 ",
			fieldType: "integer",
			want:      -7,
		},
		{
			name:      "integer parse failure",
			rawValue:  "abc",
			fieldType: "integer",
			wantErr:   true,
		},
		{
			name:      "string preserves raw value without trim",
			rawValue:  "  hello  ",
			fieldType: "string",
			want:      "  hello  ",
		},
		{
			name:      "unknown type returns error",
			rawValue:  "value",
			fieldType: "float",
			wantErr:   true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := convertValue(tt.rawValue, tt.fieldType)
			if tt.wantErr {
				if err == nil {
					t.Fatalf("convertValue(%q, %q) error = nil, want error", tt.rawValue, tt.fieldType)
				}
				return
			}
			if err != nil {
				t.Fatalf("convertValue(%q, %q) unexpected error: %v", tt.rawValue, tt.fieldType, err)
			}
			if got != tt.want {
				t.Errorf("convertValue(%q, %q) = %v (%T), want %v (%T)",
					tt.rawValue, tt.fieldType, got, got, tt.want, tt.want)
			}
		})
	}
}

func TestPositionalExtractor_Extract(t *testing.T) {
	ext := &PositionalExtractor{}

	t.Run("regular field extraction", func(t *testing.T) {
		row := decoder.NewPositionalRow(1, "T1", 20, "ABCDE12345FGHIJ")
		field := &schema.FieldDef{
			Name:  "NUM_FIELD",
			Type:  "integer",
			Start: 5,
			End:   10,
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != 12345 {
			t.Errorf("got %v, want 12345", got)
		}
	})

	t.Run("regular string field extraction", func(t *testing.T) {
		row := decoder.NewPositionalRow(1, "T1", 15, "ABCDE12345FGHIJ")
		field := &schema.FieldDef{
			Name:  "STR_FIELD",
			Type:  "string",
			Start: 0,
			End:   5,
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != "ABCDE" {
			t.Errorf("got %v, want %q", got, "ABCDE")
		}
	})

	t.Run("fill value extracts as nil", func(t *testing.T) {
		row := decoder.NewPositionalRow(1, "M5", 66, "M520181011111111177119680701WTTTP0PYZ222221122222201121112####0000")
		field := &schema.FieldDef{
			Name:  "AMOUNT_EARNED_INCOME",
			Type:  "string",
			Start: 58,
			End:   62,
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != nil {
			t.Errorf("got %v, want nil", got)
		}
	})

	t.Run("computed field via SourceField", func(t *testing.T) {
		row := decoder.NewPositionalRow(1, "T1", 10, "0000000000")
		field := &schema.FieldDef{
			Name:        "DERIVED",
			Type:        "string",
			SourceField: "ORIGIN",
		}
		extracted := MapFieldGetter{"ORIGIN": "source_value"}

		got, err := ext.Extract(row, field, nil, extracted)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != "source_value" {
			t.Errorf("got %v, want %q", got, "source_value")
		}
	})

	t.Run("computed field source not found", func(t *testing.T) {
		row := decoder.NewPositionalRow(1, "T1", 10, "0000000000")
		field := &schema.FieldDef{
			Name:        "DERIVED",
			Type:        "string",
			SourceField: "MISSING",
		}
		extracted := MapFieldGetter{}

		_, err := ext.Extract(row, field, nil, extracted)
		if err == nil {
			t.Fatal("expected error for missing source field, got nil")
		}
	})

	t.Run("with trim transform", func(t *testing.T) {
		row := decoder.NewPositionalRow(1, "T1", 10, "  42      ")
		field := &schema.FieldDef{
			Name:  "TRIMMED",
			Type:  "integer",
			Start: 0,
			End:   10,
			Transform: &schema.TransformDef{
				Name: "trim",
			},
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != 42 {
			t.Errorf("got %v, want 42", got)
		}
	})

	t.Run("with unknown transform returns error", func(t *testing.T) {
		row := decoder.NewPositionalRow(1, "T1", 10, "ABCDE12345")
		field := &schema.FieldDef{
			Name:  "BAD_TRANSFORM",
			Type:  "string",
			Start: 0,
			End:   5,
			Transform: &schema.TransformDef{
				Name: "nonexistent_transform",
			},
		}

		_, err := ext.Extract(row, field, nil, nil)
		if err == nil {
			t.Fatal("expected error for unknown transform, got nil")
		}
	})

	t.Run("wrong row type returns error", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 5, []any{"a", "b", "c"})
		field := &schema.FieldDef{
			Name:  "FIELD",
			Type:  "string",
			Start: 0,
			End:   5,
		}

		_, err := ext.Extract(row, field, nil, nil)
		if err == nil {
			t.Fatal("expected error for wrong row type, got nil")
		}
	})

	t.Run("empty slice returns nil", func(t *testing.T) {
		row := decoder.NewPositionalRow(1, "T1", 5, "     ")
		field := &schema.FieldDef{
			Name:  "BLANK",
			Type:  "integer",
			Start: 0,
			End:   5,
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != nil {
			t.Errorf("got %v, want nil", got)
		}
	})
}

func TestColumnarExtractor_Extract(t *testing.T) {
	ext := &ColumnarExtractor{}

	t.Run("regular field extraction", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 3, []any{"Alice", 42, "active"})
		field := &schema.FieldDef{
			Name:   "AGE",
			Type:   "integer",
			Column: 1,
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != 42 {
			t.Errorf("got %v, want 42", got)
		}
	})

	t.Run("regular string field extraction", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 3, []any{"Alice", 42, "active"})
		field := &schema.FieldDef{
			Name:   "NAME",
			Type:   "string",
			Column: 0,
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != "Alice" {
			t.Errorf("got %v, want %q", got, "Alice")
		}
	})

	t.Run("nil column returns nil", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 3, []any{"Alice", nil, "active"})
		field := &schema.FieldDef{
			Name:   "MISSING_COL",
			Type:   "string",
			Column: 5, // out of bounds
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != nil {
			t.Errorf("got %v, want nil", got)
		}
	})

	t.Run("computed field via SourceField", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 3, []any{"a", "b", "c"})
		field := &schema.FieldDef{
			Name:        "DERIVED",
			Type:        "string",
			SourceField: "ORIGIN",
		}
		extracted := MapFieldGetter{"ORIGIN": "computed"}

		got, err := ext.Extract(row, field, nil, extracted)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != "computed" {
			t.Errorf("got %v, want %q", got, "computed")
		}
	})

	t.Run("computed field source not found", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 3, []any{"a", "b", "c"})
		field := &schema.FieldDef{
			Name:        "DERIVED",
			Type:        "string",
			SourceField: "MISSING",
		}
		extracted := MapFieldGetter{}

		_, err := ext.Extract(row, field, nil, extracted)
		if err == nil {
			t.Fatal("expected error for missing source field, got nil")
		}
	})

	t.Run("with trim transform", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 2, []any{"  hello  ", "world"})
		field := &schema.FieldDef{
			Name:   "TRIMMED",
			Type:   "string",
			Column: 0,
			Transform: &schema.TransformDef{
				Name: "trim",
			},
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != "hello" {
			t.Errorf("got %v, want %q", got, "hello")
		}
	})

	t.Run("with unknown transform returns error", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 2, []any{"value", "other"})
		field := &schema.FieldDef{
			Name:   "BAD_TRANSFORM",
			Type:   "string",
			Column: 0,
			Transform: &schema.TransformDef{
				Name: "nonexistent_transform",
			},
		}

		_, err := ext.Extract(row, field, nil, nil)
		if err == nil {
			t.Fatal("expected error for unknown transform, got nil")
		}
	})

	t.Run("wrong row type returns error", func(t *testing.T) {
		row := decoder.NewPositionalRow(1, "T1", 10, "ABCDE12345")
		field := &schema.FieldDef{
			Name:   "FIELD",
			Type:   "string",
			Column: 0,
		}

		_, err := ext.Extract(row, field, nil, nil)
		if err == nil {
			t.Fatal("expected error for wrong row type, got nil")
		}
	})

	t.Run("integer column value", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 2, []any{99, "text"})
		field := &schema.FieldDef{
			Name:   "INT_COL",
			Type:   "integer",
			Column: 0,
		}

		got, err := ext.Extract(row, field, nil, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != 99 {
			t.Errorf("got %v, want 99", got)
		}
	})

	t.Run("computed field with integer source value", func(t *testing.T) {
		row := decoder.NewColumnarRow(1, "T1", 1, []any{"x"})
		field := &schema.FieldDef{
			Name:        "DERIVED_INT",
			Type:        "integer",
			SourceField: "SRC",
		}
		extracted := MapFieldGetter{"SRC": 123}

		got, err := ext.Extract(row, field, nil, extracted)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != 123 {
			t.Errorf("got %v, want 123", got)
		}
	})
}
