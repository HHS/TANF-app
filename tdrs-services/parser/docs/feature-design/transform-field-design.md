# TransformField Design for Go Parser

This document outlines the design for implementing Python's `TransformField` concept in the Go parser, including support for runtime context (kwargs) like the encryption flag from header records.

The design follows a **layered approach**:
1. **Layer 1: Core** - ParseContext and simple parameterized transforms
2. **Layer 2: Pipeline** - Chain multiple transforms together
3. **Layer 3: Multi-Field** - Transforms that read from multiple input fields

Each layer builds on the previous, allowing incremental implementation based on needs.

---

## Table of Contents

- [Background](#background)
- [Go Design Goals](#go-design-goals)
- [Layer 1: Core Implementation](#layer-1-core-implementation)
- [Layer 2: Pipeline Support](#layer-2-pipeline-support)
- [Layer 3: Multi-Field Support](#layer-3-multi-field-support)
- [Unified Transform Interface](#unified-transform-interface)
- [Data Flow](#data-flow)
- [Comparison Tables](#comparison-tables)
- [Testing](#testing)
- [Migration Path](#migration-path)

---

## Background

### Python Implementation

In Python, `TransformField` (defined in `parsers/fields.py`) extends the base `Field` class:

```python
class TransformField(Field):
    def __init__(self, transform_func, item, name, ..., **kwargs):
        super().__init__(...)
        self.transform_func = transform_func
        self.kwargs = kwargs  # Runtime parameters

    def parse_value(self, row):
        value = self._get_raw_value(row)
        return self.transform_func(value, **self.kwargs)
```

Key characteristics:
- Takes a `transform_func` callable that transforms the raw value
- Stores `kwargs` that are passed to the transform function
- Transform function handles all type coercion
- Supports higher-order functions (closures) for parameterized transforms

### Python Transform Examples

**1. Simple transform - `zero_pad`:**
```python
def zero_pad(digits):
    def transform(value, **kwargs):
        return value.lstrip().zfill(digits)
    return transform

# Usage in schema:
TransformField(zero_pad(3), name="COUNTY_FIPS_CODE", ...)
```

**2. Runtime context - `tanf_ssn_decryption_func`:**
```python
def tanf_ssn_decryption_func(value, **kwargs):
    if kwargs.get("is_encrypted", False):
        # Apply decryption
        return decrypted_value
    return value

# Usage - is_encrypted updated at runtime after header parsing
TransformField(tanf_ssn_decryption_func, name="SSN", is_encrypted=False, ...)
```

**3. Computed fields - `calendar_quarter_to_rpt_month_year`:**
```python
def calendar_quarter_to_rpt_month_year(month_index):
    def transform(value, **kwargs):
        year = value[:4]
        quarter = value[-1]
        month = get_month_for_quarter(quarter, month_index)
        return int(f"{year}{month}")
    return transform

# Creates RPT_MONTH_YEAR from same position as CALENDAR_QUARTER
TransformField(calendar_quarter_to_rpt_month_year(0), name="RPT_MONTH_YEAR", ...)
```

### Runtime Context Challenge

The SSN decryption requires knowing if the file has encrypted SSNs, which is determined by parsing the header record (item 9 = "E" means encrypted):

```python
# In tdr_parser.py after header parsing:
is_encrypted = field_values["encryption"] == "E"

# In schema_manager.py - mutates all TransformField kwargs:
def update_encrypted_fields(self, is_encrypted):
    for schema in self.schema_map.values():
        for field in schema.fields:
            if type(field) == TransformField and "is_encrypted" in field.kwargs:
                field.kwargs["is_encrypted"] = is_encrypted
```

---

## Go Design Goals

### Current State

The Go parser has a basic transform concept:
- `FieldDef.Transform` is a string field (e.g., `"zero_pad_3"`)
- Transforms are hardcoded in `extractor.go` as `map[string]func(string) string`
- No parameterization - separate entries for `zero_pad_3`, `zero_pad_5`
- No runtime context support

### Goals

1. **Parameterized transforms** - Single `zero_pad` with configurable digits
2. **Runtime context** - Pass header-derived values (like `IsEncrypted`) to transforms
3. **Computed fields** - Support fields derived from another field's raw value
4. **Pipeline support** - Chain multiple transforms together
5. **Multi-field transforms** - Transforms that combine multiple input fields
6. **Type safety** - Leverage Go's static typing
7. **YAML configuration** - Transforms configured in schema files, not code
8. **Testability** - Easy to test transforms in isolation
9. **Extensibility** - Easy to add new transform types without changing core interfaces

---

## Layer 1: Core Implementation

Layer 1 provides the foundation: runtime context via `ParseContext` and simple parameterized transforms.

### 1.1 ParseContext Struct

Create `internal/parser/context.go`:

```go
package parser

// ParseContext carries runtime information extracted from header
// that affects how subsequent records are parsed.
type ParseContext struct {
    // IsEncrypted indicates whether SSN fields need decryption.
    // Determined by header item 9 (encryption indicator = "E").
    IsEncrypted bool

    // Add other header-derived values as needed:
    // TribeCode    string
    // StateFips    string
    // RptMonthYear int
}
```

### 1.2 TransformDef Struct

Update `internal/schema/types.go`:

```go
// TransformDef defines a field transformation with optional parameters.
type TransformDef struct {
    // Name is the transform function name (e.g., "zero_pad", "ssn_decrypt")
    Name string `yaml:"name"`

    // Params contains static configuration from the schema YAML.
    // These are known at schema load time, not runtime.
    Params map[string]any `yaml:"params,omitempty"`
}

// FieldDef represents a single field in a schema.
type FieldDef struct {
    Name         string `yaml:"name"`
    Item         string `yaml:"item"`
    FriendlyName string `yaml:"friendly_name"`
    Type         string `yaml:"type"`
    Required     bool   `yaml:"required"`
    Start        int    `yaml:"start,omitempty"`
    End          int    `yaml:"end,omitempty"`
    Column       int    `yaml:"column,omitempty"`
    ColumnHeader string `yaml:"column_header,omitempty"`

    // Transform defines an optional transformation to apply to the raw value.
    Transform *TransformDef `yaml:"transform,omitempty"`

    // SourceField references another field's raw value for computed fields.
    // If set, the raw value comes from the named field instead of Start/End.
    SourceField string `yaml:"source_field,omitempty"`
}
```

### 1.3 Transform Function Interface

Create `internal/transform/transform.go`:

```go
package transform

import (
    "fmt"
    "strings"

    "go-parser/internal/parser"
)

// TransformFunc defines the signature for all transform functions.
// Parameters:
//   - value: raw string extracted from the field position
//   - params: static configuration from schema YAML (e.g., digits for zero_pad)
//   - ctx: runtime context from header parsing (e.g., IsEncrypted)
//
// Returns the transformed string value and any error.
type TransformFunc func(value string, params map[string]any, ctx *parser.ParseContext) (string, error)

// Registry maps transform names to their implementations.
var Registry = map[string]TransformFunc{
    "trim":                      Trim,
    "zero_pad":                  ZeroPad,
    "ssn_decrypt":               SSNDecrypt,
    "calendar_quarter_to_month": CalendarQuarterToMonth,
}

// Apply looks up and executes a transform by name.
func Apply(name, value string, params map[string]any, ctx *parser.ParseContext) (string, error) {
    fn, ok := Registry[name]
    if !ok {
        return "", fmt.Errorf("unknown transform: %s", name)
    }
    return fn(value, params, ctx)
}

// Trim removes leading and trailing whitespace.
func Trim(value string, _ map[string]any, _ *parser.ParseContext) (string, error) {
    return strings.TrimSpace(value), nil
}

// ZeroPad pads a string with leading zeros to reach the specified length.
// Params:
//   - digits (int): target length after padding
func ZeroPad(value string, params map[string]any, _ *parser.ParseContext) (string, error) {
    digits, ok := params["digits"].(int)
    if !ok {
        return "", fmt.Errorf("zero_pad requires 'digits' param (int)")
    }

    trimmed := strings.TrimLeft(value, " ")
    if len(trimmed) >= digits {
        return trimmed, nil
    }
    return fmt.Sprintf("%0*s", digits, trimmed), nil
}

// SSNDecrypt decrypts TANF/SSP SSN values using character substitution.
// The encryption status is determined by:
//   1. Runtime context (ctx.IsEncrypted) - from header parsing
//   2. Static param override (params["encrypted"]) - for testing
//
// Params (optional):
//   - encrypted (bool): force encryption status, overrides runtime context
func SSNDecrypt(value string, params map[string]any, ctx *parser.ParseContext) (string, error) {
    if value == "" {
        return "", nil
    }

    // Determine encryption status
    // Priority: static param > runtime context > default (false)
    encrypted := false
    if ctx != nil {
        encrypted = ctx.IsEncrypted
    }
    if enc, ok := params["encrypted"].(bool); ok {
        encrypted = enc // Static override
    }

    if !encrypted {
        return value, nil
    }

    // TANF SSN decryption mapping
    decryptMap := map[rune]rune{
        '@': '1', '9': '2', 'Z': '3', 'P': '4', '0': '5',
        '#': '6', 'Y': '7', 'B': '8', 'W': '9', 'T': '0',
    }

    var result strings.Builder
    result.Grow(len(value))
    for _, c := range value {
        if decrypted, ok := decryptMap[c]; ok {
            result.WriteRune(decrypted)
        } else {
            result.WriteRune(c)
        }
    }
    return result.String(), nil
}

// CalendarQuarterToMonth converts a calendar quarter (YYYYQ) to year-month (YYYYMM).
// Params:
//   - month_index (int): which month in the quarter (0=first, 1=second, 2=third)
func CalendarQuarterToMonth(value string, params map[string]any, _ *parser.ParseContext) (string, error) {
    monthIndex, ok := params["month_index"].(int)
    if !ok {
        return "", fmt.Errorf("calendar_quarter_to_month requires 'month_index' param (int)")
    }

    if len(value) < 5 {
        return "", fmt.Errorf("invalid quarter format (expected YYYYQ): %s", value)
    }

    year := strings.TrimSpace(value[:4])
    quarter := value[len(value)-1]

    quarterMonths := map[byte][]string{
        '1': {"01", "02", "03"}, // Q1: Jan, Feb, Mar
        '2': {"04", "05", "06"}, // Q2: Apr, May, Jun
        '3': {"07", "08", "09"}, // Q3: Jul, Aug, Sep
        '4': {"10", "11", "12"}, // Q4: Oct, Nov, Dec
    }

    months, ok := quarterMonths[quarter]
    if !ok {
        return "", fmt.Errorf("invalid quarter digit: %c", quarter)
    }

    if monthIndex < 0 || monthIndex >= 3 {
        return "", fmt.Errorf("month_index must be 0, 1, or 2: got %d", monthIndex)
    }

    return year + months[monthIndex], nil
}
```

### 1.4 Updated FieldExtractor

Update `internal/parser/extractor.go`:

```go
package parser

import (
    "fmt"
    "strconv"
    "strings"

    "go-parser/internal/decoder"
    "go-parser/internal/schema"
    "go-parser/internal/transform"
)

// FieldExtractor extracts field values from rows based on the file format.
type FieldExtractor interface {
    // Extract extracts a field value from a row.
    // ctx may be nil if no runtime context is available.
    Extract(row decoder.Row, field *schema.FieldDef, ctx *ParseContext) (any, error)

    // ExtractWithSource extracts a field that derives its raw value from another field.
    // extractedFields contains already-parsed fields for source lookups.
    ExtractWithSource(
        row decoder.Row,
        field *schema.FieldDef,
        ctx *ParseContext,
        extractedFields map[string]any,
    ) (any, error)
}

// PositionalExtractor extracts fields from positional (fixed-width) rows.
type PositionalExtractor struct{}

func (e *PositionalExtractor) Extract(
    row decoder.Row,
    field *schema.FieldDef,
    ctx *ParseContext,
) (any, error) {
    pr, ok := row.(*decoder.PositionalRow)
    if !ok {
        return nil, fmt.Errorf("expected PositionalRow, got %T", row)
    }

    // Extract raw string value using byte positions
    rawValue := pr.Slice(field.Start, field.End)

    // Apply transformation if specified
    if field.Transform != nil {
        transformed, err := transform.Apply(
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

func (e *PositionalExtractor) ExtractWithSource(
    row decoder.Row,
    field *schema.FieldDef,
    ctx *ParseContext,
    extractedFields map[string]any,
) (any, error) {
    var rawValue string

    if field.SourceField != "" {
        // Computed field - get raw value from already-extracted field
        src, ok := extractedFields[field.SourceField]
        if !ok {
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
        transformed, err := transform.Apply(
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
```

### 1.5 Updated Worker Pool

Update `internal/worker/pool.go`:

```go
// Pool manages worker goroutines for parallel parsing.
type Pool struct {
    numWorkers int
    extractor  parser.FieldExtractor
    parseCtx   *parser.ParseContext // Runtime context from header

    work    chan *processor.Batch
    results chan *ParsedBatch
    wg      sync.WaitGroup
}

// SetParseContext sets the runtime context after header parsing.
// Must be called before processing data records.
func (p *Pool) SetParseContext(ctx *parser.ParseContext) {
    p.parseCtx = ctx
}

// parseRow passes context to extractor
func (p *Pool) parseRow(line processor.RawLine) ([]*ParsedRecord, error) {
    // ... existing setup code ...

    // Parse shared fields with context
    for i := range line.Schema.Shared {
        field := &line.Schema.Shared[i]
        value, err := p.extractor.Extract(line.Row, field, p.parseCtx)
        if err != nil {
            continue
        }
        if value != nil {
            sharedFields[field.Name] = value
        }
    }

    // Parse segment fields with context
    for segIdx, segment := range line.Schema.Segments {
        // ...
        for i := range segment.Fields {
            field := &segment.Fields[i]
            value, err := p.extractor.Extract(line.Row, field, p.parseCtx)
            // ...
        }
    }
    // ...
}
```

### 1.6 Layer 1 Schema YAML Examples

**Zero padding with parameter:**
```yaml
# config/schemas/tanf/t1.yaml
- name: COUNTY_FIPS_CODE
  item: "10"
  friendly_name: "County FIPS Code"
  type: string
  start: 25
  end: 28
  transform:
    name: zero_pad
    params:
      digits: 3
```

**SSN decryption (runtime context):**
```yaml
# config/schemas/tanf/t2.yaml
- name: SSN
  item: "33"
  friendly_name: "Social Security Number"
  type: string
  start: 29
  end: 38
  required: true
  transform:
    name: ssn_decrypt
    # No 'encrypted' param - determined at runtime from header
    # Can add `params: { encrypted: true }` to force for testing
```

**Computed field from same source:**
```yaml
# config/schemas/tanf/t6.yaml
shared:
  - name: RecordType
    item: "2"
    type: string
    start: 0
    end: 2

  - name: CALENDAR_QUARTER
    item: "4"
    friendly_name: "Calendar Quarter"
    type: string
    start: 2
    end: 7

  - name: RPT_MONTH_YEAR
    item: "4"
    friendly_name: "Reporting Year and Month"
    type: integer
    source_field: CALENDAR_QUARTER  # Use same raw value
    transform:
      name: calendar_quarter_to_month
      params:
        month_index: 0  # First month of quarter for segment 1
```

---

## Layer 2: Pipeline Support

Layer 2 adds the ability to chain multiple transforms together. This is useful when a field needs multiple processing steps (e.g., trim whitespace, then pad with zeros).

### 2.1 Extended TransformDef

Update `internal/schema/types.go` to support pipelines:

```go
// TransformDef defines a field transformation.
// Either Name (single transform) or Pipeline (multiple transforms) should be set.
type TransformDef struct {
    // Name is the transform function name for single transforms.
    Name string `yaml:"name,omitempty"`

    // Params contains static configuration for the transform.
    Params map[string]any `yaml:"params,omitempty"`

    // Pipeline defines a sequence of transforms to apply in order.
    // Each step's output becomes the next step's input.
    Pipeline []TransformStep `yaml:"pipeline,omitempty"`
}

// TransformStep represents a single step in a transform pipeline.
type TransformStep struct {
    Name   string         `yaml:"name"`
    Params map[string]any `yaml:"params,omitempty"`
}

// IsPipeline returns true if this is a pipeline transform.
func (t *TransformDef) IsPipeline() bool {
    return len(t.Pipeline) > 0
}
```

### 2.2 Pipeline Execution

Update `internal/transform/transform.go`:

```go
// ApplyTransform handles both single transforms and pipelines.
func ApplyTransform(def *schema.TransformDef, value string, ctx *parser.ParseContext) (string, error) {
    if def == nil {
        return value, nil
    }

    if def.IsPipeline() {
        return ApplyPipeline(def.Pipeline, value, ctx)
    }

    return Apply(def.Name, value, def.Params, ctx)
}

// ApplyPipeline executes a sequence of transforms, passing each output to the next input.
func ApplyPipeline(steps []schema.TransformStep, value string, ctx *parser.ParseContext) (string, error) {
    result := value

    for i, step := range steps {
        transformed, err := Apply(step.Name, result, step.Params, ctx)
        if err != nil {
            return "", fmt.Errorf("pipeline step %d (%s) failed: %w", i+1, step.Name, err)
        }
        result = transformed
    }

    return result, nil
}
```

### 2.3 Updated Extractor for Pipelines

Update extraction to use the unified `ApplyTransform`:

```go
func (e *PositionalExtractor) Extract(
    row decoder.Row,
    field *schema.FieldDef,
    ctx *ParseContext,
) (any, error) {
    pr, ok := row.(*decoder.PositionalRow)
    if !ok {
        return nil, fmt.Errorf("expected PositionalRow, got %T", row)
    }

    rawValue := pr.Slice(field.Start, field.End)

    // Apply transformation (single or pipeline)
    if field.Transform != nil {
        transformed, err := transform.ApplyTransform(field.Transform, rawValue, ctx)
        if err != nil {
            return nil, fmt.Errorf("transform on field %s failed: %w", field.Name, err)
        }
        rawValue = transformed
    }

    return convertValue(rawValue, field.Type)
}
```

### 2.4 Layer 2 Schema YAML Examples

**Pipeline: trim then zero-pad:**
```yaml
- name: COUNTY_FIPS_CODE
  item: "10"
  friendly_name: "County FIPS Code"
  type: string
  start: 25
  end: 28
  transform:
    pipeline:
      - name: trim
      - name: zero_pad
        params:
          digits: 3
```

**Pipeline: decrypt then validate format:**
```yaml
- name: SSN
  item: "33"
  friendly_name: "Social Security Number"
  type: string
  start: 29
  end: 38
  transform:
    pipeline:
      - name: ssn_decrypt
      - name: trim
```

**Complex pipeline with multiple steps:**
```yaml
- name: PROCESSED_VALUE
  type: string
  start: 10
  end: 20
  transform:
    pipeline:
      - name: trim
      - name: uppercase
      - name: replace
        params:
          old: "-"
          new: ""
      - name: zero_pad
        params:
          digits: 10
```

### 2.5 Additional Transform Functions for Pipelines

```go
// Uppercase converts string to uppercase.
func Uppercase(value string, _ map[string]any, _ *parser.ParseContext) (string, error) {
    return strings.ToUpper(value), nil
}

// Lowercase converts string to lowercase.
func Lowercase(value string, _ map[string]any, _ *parser.ParseContext) (string, error) {
    return strings.ToLower(value), nil
}

// Replace replaces occurrences of a substring.
// Params:
//   - old (string): substring to find
//   - new (string): replacement string
//   - count (int, optional): max replacements (-1 for all, default)
func Replace(value string, params map[string]any, _ *parser.ParseContext) (string, error) {
    old, ok := params["old"].(string)
    if !ok {
        return "", fmt.Errorf("replace requires 'old' param (string)")
    }

    newStr, ok := params["new"].(string)
    if !ok {
        return "", fmt.Errorf("replace requires 'new' param (string)")
    }

    count := -1 // Replace all by default
    if c, ok := params["count"].(int); ok {
        count = c
    }

    return strings.Replace(value, old, newStr, count), nil
}

// TrimPrefix removes a prefix from the string.
// Params:
//   - prefix (string): prefix to remove
func TrimPrefix(value string, params map[string]any, _ *parser.ParseContext) (string, error) {
    prefix, ok := params["prefix"].(string)
    if !ok {
        return "", fmt.Errorf("trim_prefix requires 'prefix' param (string)")
    }
    return strings.TrimPrefix(value, prefix), nil
}

// Substring extracts a portion of the string.
// Params:
//   - start (int): start index (inclusive)
//   - end (int, optional): end index (exclusive), defaults to end of string
func Substring(value string, params map[string]any, _ *parser.ParseContext) (string, error) {
    start, ok := params["start"].(int)
    if !ok {
        return "", fmt.Errorf("substring requires 'start' param (int)")
    }

    if start < 0 || start > len(value) {
        return "", fmt.Errorf("substring start index out of range: %d", start)
    }

    end := len(value)
    if e, ok := params["end"].(int); ok {
        if e < start || e > len(value) {
            return "", fmt.Errorf("substring end index out of range: %d", e)
        }
        end = e
    }

    return value[start:end], nil
}

// Register additional transforms
func init() {
    Registry["uppercase"] = Uppercase
    Registry["lowercase"] = Lowercase
    Registry["replace"] = Replace
    Registry["trim_prefix"] = TrimPrefix
    Registry["substring"] = Substring
}
```

---

## Layer 3: Multi-Field Support

Layer 3 adds support for transforms that need to read from multiple input fields. This is useful for computed fields like `RPT_MONTH_YEAR` that combine `year` and `quarter` from the header.

### 3.1 Multi-Field Transform Types

Update `internal/schema/types.go`:

```go
// TransformDef defines a field transformation.
type TransformDef struct {
    // Single transform
    Name   string         `yaml:"name,omitempty"`
    Params map[string]any `yaml:"params,omitempty"`

    // Pipeline of transforms
    Pipeline []TransformStep `yaml:"pipeline,omitempty"`

    // Multi-field transform (Layer 3)
    Inputs []string `yaml:"inputs,omitempty"`
}

// IsMultiField returns true if this transform requires multiple input fields.
func (t *TransformDef) IsMultiField() bool {
    return len(t.Inputs) > 0
}
```

### 3.2 Multi-Field Transform Function Signature

Create `internal/transform/multifield.go`:

```go
package transform

import (
    "fmt"
    "go-parser/internal/parser"
    "go-parser/internal/schema"
)

// MultiFieldTransformFunc defines the signature for transforms that read multiple fields.
// Parameters:
//   - inputs: map of field name to field value for all input fields
//   - params: static configuration from schema YAML
//   - ctx: runtime context from header parsing
//
// Returns the computed value (can be any type) and any error.
type MultiFieldTransformFunc func(
    inputs map[string]any,
    params map[string]any,
    ctx *parser.ParseContext,
) (any, error)

// MultiFieldRegistry maps transform names to multi-field implementations.
var MultiFieldRegistry = map[string]MultiFieldTransformFunc{
    "combine_year_quarter": CombineYearQuarter,
    "concat":               Concat,
    "coalesce":             Coalesce,
}

// ApplyMultiField executes a multi-field transform.
func ApplyMultiField(
    def *schema.TransformDef,
    allFields map[string]any,
    ctx *parser.ParseContext,
) (any, error) {
    // Gather input values
    inputs := make(map[string]any, len(def.Inputs))
    for _, fieldName := range def.Inputs {
        value, ok := allFields[fieldName]
        if !ok {
            return nil, fmt.Errorf("multi-field transform: input field %s not found", fieldName)
        }
        inputs[fieldName] = value
    }

    fn, ok := MultiFieldRegistry[def.Name]
    if !ok {
        return nil, fmt.Errorf("unknown multi-field transform: %s", def.Name)
    }

    return fn(inputs, def.Params, ctx)
}

// CombineYearQuarter combines year and quarter fields into YYYYMM format.
// Inputs: year (int), quarter (string)
// Params:
//   - month_index (int): which month in the quarter (0=first, 1=second, 2=third)
func CombineYearQuarter(
    inputs map[string]any,
    params map[string]any,
    _ *parser.ParseContext,
) (any, error) {
    year, ok := inputs["year"].(int)
    if !ok {
        return nil, fmt.Errorf("combine_year_quarter: 'year' must be int")
    }

    quarter, ok := inputs["quarter"].(string)
    if !ok {
        return nil, fmt.Errorf("combine_year_quarter: 'quarter' must be string")
    }

    monthIndex, ok := params["month_index"].(int)
    if !ok {
        return nil, fmt.Errorf("combine_year_quarter requires 'month_index' param")
    }

    quarterMonths := map[string][]string{
        "1": {"01", "02", "03"},
        "2": {"04", "05", "06"},
        "3": {"07", "08", "09"},
        "4": {"10", "11", "12"},
    }

    months, ok := quarterMonths[quarter]
    if !ok {
        return nil, fmt.Errorf("invalid quarter: %s", quarter)
    }

    if monthIndex < 0 || monthIndex >= 3 {
        return nil, fmt.Errorf("month_index must be 0, 1, or 2: got %d", monthIndex)
    }

    // Return as integer YYYYMM
    return fmt.Sprintf("%d%s", year, months[monthIndex]), nil
}

// Concat concatenates multiple field values with an optional separator.
// Inputs: any fields listed in the inputs array
// Params:
//   - separator (string, optional): separator between values (default: "")
//   - order ([]string, optional): explicit order of fields (default: inputs order)
func Concat(
    inputs map[string]any,
    params map[string]any,
    _ *parser.ParseContext,
) (any, error) {
    separator := ""
    if sep, ok := params["separator"].(string); ok {
        separator = sep
    }

    // Determine order
    var order []string
    if o, ok := params["order"].([]any); ok {
        for _, v := range o {
            if s, ok := v.(string); ok {
                order = append(order, s)
            }
        }
    }

    // If no explicit order, use inputs map (note: map order is not guaranteed)
    if len(order) == 0 {
        for k := range inputs {
            order = append(order, k)
        }
    }

    var parts []string
    for _, fieldName := range order {
        if val, ok := inputs[fieldName]; ok {
            parts = append(parts, fmt.Sprintf("%v", val))
        }
    }

    return strings.Join(parts, separator), nil
}

// Coalesce returns the first non-nil, non-empty value from the inputs.
// Inputs: fields to check in order
// Params:
//   - order ([]string): explicit order to check fields
func Coalesce(
    inputs map[string]any,
    params map[string]any,
    _ *parser.ParseContext,
) (any, error) {
    order, ok := params["order"].([]any)
    if !ok {
        return nil, fmt.Errorf("coalesce requires 'order' param (list of field names)")
    }

    for _, v := range order {
        fieldName, ok := v.(string)
        if !ok {
            continue
        }

        val, exists := inputs[fieldName]
        if !exists {
            continue
        }

        // Check if non-nil and non-empty
        if val == nil {
            continue
        }
        if str, ok := val.(string); ok && str == "" {
            continue
        }

        return val, nil
    }

    return nil, nil
}
```

### 3.3 Updated Extractor for Multi-Field

```go
// ExtractAll extracts all fields from a row, handling dependencies correctly.
// Multi-field transforms are processed after their input fields.
func (e *PositionalExtractor) ExtractAll(
    row decoder.Row,
    fields []schema.FieldDef,
    ctx *ParseContext,
) (map[string]any, error) {
    result := make(map[string]any, len(fields))

    // First pass: extract all non-multi-field transforms
    var multiFieldDefs []schema.FieldDef
    for _, field := range fields {
        if field.Transform != nil && field.Transform.IsMultiField() {
            multiFieldDefs = append(multiFieldDefs, field)
            continue
        }

        value, err := e.ExtractWithSource(row, &field, ctx, result)
        if err != nil {
            return nil, err
        }
        if value != nil {
            result[field.Name] = value
        }
    }

    // Second pass: process multi-field transforms
    for _, field := range multiFieldDefs {
        value, err := transform.ApplyMultiField(field.Transform, result, ctx)
        if err != nil {
            return nil, fmt.Errorf("multi-field transform on %s failed: %w", field.Name, err)
        }
        if value != nil {
            result[field.Name] = value
        }
    }

    return result, nil
}
```

### 3.4 Layer 3 Schema YAML Examples

**Combine year and quarter from header fields:**
```yaml
# config/schemas/tanf/t6.yaml
shared:
  - name: RecordType
    item: "2"
    type: string
    start: 0
    end: 2

  # These fields are extracted from header but available in context
  - name: RPT_MONTH_YEAR
    item: "4"
    friendly_name: "Reporting Year and Month"
    type: string
    transform:
      name: combine_year_quarter
      inputs: [year, quarter]  # References header fields
      params:
        month_index: 0
```

**Concatenate multiple fields:**
```yaml
- name: FULL_ADDRESS
  type: string
  transform:
    name: concat
    inputs: [STREET, CITY, STATE, ZIP]
    params:
      separator: ", "
      order: [STREET, CITY, STATE, ZIP]
```

**Coalesce - use first non-empty value:**
```yaml
- name: CONTACT_PHONE
  type: string
  transform:
    name: coalesce
    inputs: [MOBILE_PHONE, HOME_PHONE, WORK_PHONE]
    params:
      order: [MOBILE_PHONE, HOME_PHONE, WORK_PHONE]
```

---

## Unified Transform Interface

To simplify the extraction logic, we can create a unified interface that handles all transform types:

```go
// TransformExecutor handles all types of transforms.
type TransformExecutor struct {
    ctx *parser.ParseContext
}

// NewTransformExecutor creates a new executor with the given context.
func NewTransformExecutor(ctx *parser.ParseContext) *TransformExecutor {
    return &TransformExecutor{ctx: ctx}
}

// Execute applies a transform definition to produce a value.
// For single/pipeline transforms: value is the raw field value.
// For multi-field transforms: value is ignored, allFields is used.
func (e *TransformExecutor) Execute(
    def *schema.TransformDef,
    value string,
    allFields map[string]any,
) (any, error) {
    if def == nil {
        return value, nil
    }

    switch {
    case def.IsMultiField():
        return ApplyMultiField(def, allFields, e.ctx)
    case def.IsPipeline():
        return ApplyPipeline(def.Pipeline, value, e.ctx)
    default:
        return Apply(def.Name, value, def.Params, e.ctx)
    }
}
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Load Schemas                                                 │
│    - Parse YAML files                                           │
│    - TransformDef contains:                                     │
│      • name + params (Layer 1)                                  │
│      • pipeline steps (Layer 2)                                 │
│      • inputs for multi-field (Layer 3)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Parse Header Record                                          │
│    - Extract year, quarter, encryption indicator                │
│    - Create ParseContext{IsEncrypted: encryption == "E"}        │
│    - Store header fields for multi-field transforms             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Initialize Worker Pool                                       │
│    - pool.SetParseContext(ctx)                                  │
│    - Context includes header-derived values                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Parse Data Records                                           │
│    For each field:                                              │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ Is Multi-Field Transform?                               │  │
│    │   YES → Defer until all inputs are extracted            │  │
│    │   NO  → Extract raw value from row position             │  │
│    └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ Has Transform?                                          │  │
│    │   YES → Apply transform (single or pipeline)            │  │
│    │   NO  → Use raw value                                   │  │
│    └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ Convert to target type (string, integer)                │  │
│    └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Process Deferred Multi-Field Transforms                      │
│    - All input fields now available                             │
│    - Execute multi-field transform with inputs map              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Comparison Tables

### Python vs Go

| Aspect | Python | Go |
|--------|--------|-----|
| **Transform definition** | Callable passed to constructor | Name string + params in YAML |
| **Parameterization** | Higher-order functions (closures) | `params` map in schema |
| **Runtime context** | `kwargs` dict, mutated at runtime | `ParseContext` struct, set once |
| **Type safety** | Dynamic typing | Static `ParseContext` struct |
| **Context update** | Mutate `field.kwargs` after header | `pool.SetParseContext()` |
| **Computed fields** | Same `startIndex`/`endIndex` | `source_field` or `inputs` |
| **Pipelines** | Nested function calls | `pipeline` array in YAML |
| **Multi-field** | Not directly supported | `inputs` array in YAML |

### Layer Comparison

| Feature | Layer 1 | Layer 2 | Layer 3 |
|---------|---------|---------|---------|
| **Complexity** | Low | Medium | Medium-High |
| **Use Case** | Single-field transforms | Multi-step processing | Cross-field calculations |
| **YAML Config** | `name` + `params` | `pipeline` array | `inputs` array |
| **Transform Signature** | `func(string, params, ctx)` | Same as Layer 1 | `func(map[string]any, params, ctx)` |
| **Execution Order** | Immediate | Sequential steps | After all inputs ready |
| **Examples** | `zero_pad`, `ssn_decrypt` | trim → pad → validate | `combine_year_quarter` |

### Transform Pattern Decision Matrix

| Scenario | Recommended Approach |
|----------|---------------------|
| Simple string manipulation | Layer 1: Single transform |
| Multiple processing steps | Layer 2: Pipeline |
| Combine multiple fields | Layer 3: Multi-field |
| Context-dependent logic | Layer 1: Use `ParseContext` |
| Same source, different output | Layer 1: `source_field` |
| Complex conditional logic | Layer 1: Custom transform function |

---

## Testing

### Layer 1 Tests

```go
func TestSSNDecrypt(t *testing.T) {
    tests := []struct {
        name     string
        value    string
        params   map[string]any
        ctx      *parser.ParseContext
        expected string
    }{
        {
            name:     "not encrypted - no context",
            value:    "@90#Y0B",
            params:   nil,
            ctx:      nil,
            expected: "@90#Y0B",
        },
        {
            name:     "encrypted via context",
            value:    "@90#Y0B",
            params:   nil,
            ctx:      &parser.ParseContext{IsEncrypted: true},
            expected: "1256758",
        },
        {
            name:     "static param overrides context",
            value:    "@90#Y0B",
            params:   map[string]any{"encrypted": true},
            ctx:      &parser.ParseContext{IsEncrypted: false},
            expected: "1256758",
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := transform.SSNDecrypt(tt.value, tt.params, tt.ctx)
            require.NoError(t, err)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

### Layer 2 Tests

```go
func TestPipeline(t *testing.T) {
    pipeline := []schema.TransformStep{
        {Name: "trim"},
        {Name: "zero_pad", Params: map[string]any{"digits": 5}},
    }

    result, err := transform.ApplyPipeline(pipeline, "  42  ", nil)
    require.NoError(t, err)
    assert.Equal(t, "00042", result)
}

func TestPipelineErrorPropagation(t *testing.T) {
    pipeline := []schema.TransformStep{
        {Name: "trim"},
        {Name: "unknown_transform"}, // Should fail
    }

    _, err := transform.ApplyPipeline(pipeline, "test", nil)
    require.Error(t, err)
    assert.Contains(t, err.Error(), "step 2")
}
```

### Layer 3 Tests

```go
func TestCombineYearQuarter(t *testing.T) {
    tests := []struct {
        name       string
        inputs     map[string]any
        monthIndex int
        expected   string
    }{
        {
            name:       "Q1 first month",
            inputs:     map[string]any{"year": 2024, "quarter": "1"},
            monthIndex: 0,
            expected:   "202401",
        },
        {
            name:       "Q3 third month",
            inputs:     map[string]any{"year": 2024, "quarter": "3"},
            monthIndex: 2,
            expected:   "202409",
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            params := map[string]any{"month_index": tt.monthIndex}
            result, err := transform.CombineYearQuarter(tt.inputs, params, nil)
            require.NoError(t, err)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

---

## Migration Path

### Phase 1: Layer 1 (Core)

1. Add `ParseContext` struct to `internal/parser/context.go`
2. Update `TransformDef` in `internal/schema/types.go`
3. Create `internal/transform/transform.go` with new function signature
4. Update `FieldExtractor` interface to accept context
5. Update `Pool` to store and pass context
6. Migrate existing transforms (`zero_pad_3`, `zero_pad_5`) to parameterized `zero_pad`
7. Add `ssn_decrypt` and `calendar_quarter_to_month` transforms
8. Update schema YAML files to use new transform format

### Phase 2: Layer 2 (Pipelines)

1. Extend `TransformDef` with `Pipeline` field
2. Add `ApplyPipeline` function
3. Add utility transforms (`trim`, `uppercase`, `replace`, etc.)
4. Update extraction to handle pipelines
5. Add pipeline-based schemas where beneficial

### Phase 3: Layer 3 (Multi-Field)

1. Extend `TransformDef` with `Inputs` field
2. Create `internal/transform/multifield.go`
3. Add `MultiFieldTransformFunc` type and registry
4. Update extraction to handle two-pass processing
5. Implement `combine_year_quarter`, `concat`, `coalesce`
6. Update schemas to use multi-field transforms where needed

### Deprecation

After all phases are complete:
1. Remove legacy string-based `Transform` field support
2. Remove hardcoded `zero_pad_3`, `zero_pad_5` transforms
3. Update documentation and examples

---

## Benefits of This Design

1. **Explicit data flow** - Context is passed through function signatures, not hidden state
2. **Type-safe** - `ParseContext` is a defined struct with known fields
3. **Testable** - Easy to create mock contexts and test transforms in isolation
4. **Extensible** - Add new transforms or layers without changing core interfaces
5. **No mutation** - Context is set once after header, never mutated during parsing
6. **Go idiomatic** - Uses explicit parameter passing vs Python's dynamic mutation
7. **Separation of concerns** - Static params (schema) vs runtime context (header) clearly separated
8. **Composable** - Pipelines allow building complex transforms from simple ones
9. **Declarative** - Transform logic defined in YAML, not scattered in code
10. **Incremental adoption** - Each layer can be implemented independently
