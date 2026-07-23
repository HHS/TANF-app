package main

import (
	"bytes"
	"embed"
	"fmt"
	"log"
	"os"
	"sort"
	"strings"
	"text/template"
	"time"

	"github.com/alecthomas/kong"

	"go-parser/internal/config"
	"go-parser/internal/config/schema"
	"go-parser/internal/validation"
)

//go:embed templates/*.tmpl
var templateFS embed.FS

// CLI defines the command-line flags for docgen.
type CLI struct {
	ConfigFile string `kong:"type=path,default='config/parser.yaml',short='c',help='Path to parser config file',name='config-file'"`
	Output     string `kong:"short='o',help='Output file path (default: stdout)',name='output'"`
	FileSpec   string `kong:"help='Filter to a single filespec (e.g. TANF:1)',name='filespec'"`
	Record     string `kong:"help='Filter to a single record type (e.g. T1)',name='record'"`
}

// --- Doc model ---

// DocModel is the top-level documentation structure.
type DocModel struct {
	GeneratedAt string
	Header      *RecordDoc // Shared header record (common/header), rendered once at the top
	FileSpecs   []FileSpecDoc
}

// FileSpecDoc documents a single filespec (program + section).
type FileSpecDoc struct {
	Key         string
	Program     string
	Section     int
	Description string
	Records     []RecordDoc
	Group       []ValidatorDoc
}

// RecordDoc documents a single record type within a filespec.
type RecordDoc struct {
	RecordType  string
	SchemaPath  string
	Description string
	Fields      []FieldDoc
	PreCheck    []ValidatorDoc
	CrossField  []ValidatorDoc
}

// FieldDoc documents a single field within a record.
type FieldDoc struct {
	Name         string
	Item         string
	FriendlyName string
	Type         string
	Required     bool
	Validators   []ValidatorDoc
}

// ValidatorDoc documents a single validator invocation.
type ValidatorDoc struct {
	Description string
	ErrorType   string
	Message     string // Rendered example message (not raw template)
	Fields      []string
}

func main() {
	cli := &CLI{}
	parser, err := kong.New(cli,
		kong.Name("docgen"),
		kong.Description("Generate validation error documentation from parser configuration"),
		kong.UsageOnError(),
	)
	if err != nil {
		log.Fatalf("Failed to create CLI parser: %v", err)
	}

	_, err = parser.Parse(os.Args[1:])
	if err != nil {
		log.Fatalf("Failed to parse CLI: %v", err)
	}

	cfg, err := config.LoadConfig(cli.ConfigFile)
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	reg, err := config.NewRegistry(cfg)
	if err != nil {
		log.Fatalf("Failed to load registry: %v", err)
	}

	validators, err := validation.NewRegistry(cfg, reg)
	if err != nil {
		log.Fatalf("Failed to load validators: %v", err)
	}

	model := buildDocModel(reg, validators, cli.FileSpec, cli.Record)

	output, err := renderHTML(model)
	if err != nil {
		log.Fatalf("Failed to render output: %v", err)
	}

	if cli.Output != "" {
		if err := os.WriteFile(cli.Output, []byte(output), 0644); err != nil {
			log.Fatalf("Failed to write output file: %v", err)
		}
		fmt.Fprintf(os.Stderr, "Wrote output to %s\n", cli.Output)
	} else {
		fmt.Print(output)
	}
}

// --- Message rendering ---

// renderMessage executes a compiled validator's message template with a synthetic context.
// This produces an example of what the error message looks like at runtime.
func renderMessage(cv *validation.CompiledValidator, recordType string, field *schema.FieldDef) string {
	if cv.Message == nil {
		return ""
	}

	ctx := map[string]any{
		"RecordType":   recordType,
		"LineNumber":   "{line}",
		"RecordLength": "{length}",
	}

	if field != nil {
		ctx["Item"] = field.Item
		ctx["FriendlyName"] = field.FriendlyName
		ctx["Value"] = "{value}"
	}

	if len(cv.Params) > 0 {
		ctx["Params"] = cv.Params
	}

	if len(cv.Fields) > 0 {
		ctx["Fields"] = cv.Fields
	}

	var buf bytes.Buffer
	if err := cv.Message.Execute(&buf, ctx); err != nil {
		// Fall back to raw template text if rendering fails
		if cv.Message.Tree != nil && cv.Message.Tree.Root != nil {
			return cv.Message.Tree.Root.String()
		}
		return cv.ID
	}
	return buf.String()
}

// friendlyErrorType returns a human-readable label for an error type code.
func friendlyErrorType(errorType string) string {
	switch errorType {
	case validation.ErrorTypeRecordPreCheck:
		return "Blocks record processing"
	case validation.ErrorTypeFieldValue:
		return "Field value error"
	case validation.ErrorTypeValueConsistency:
		return "Cross-field consistency error"
	case validation.ErrorTypeCaseConsistency:
		return "Blocks case processing"
	default:
		return errorType
	}
}

// --- Doc model building ---

func buildDocModel(reg *config.Registry, validators *validation.ValidatorRegistry, filterFileSpec, filterRecord string) *DocModel {
	model := &DocModel{
		GeneratedAt: time.Now().UTC().Format(time.RFC3339),
	}

	// Build the shared header record once (used by all programs except FRA)
	if cs := reg.GetSchema("common/header"); cs != nil {
		header := buildRecordDoc(cs, "common/header", validators)
		model.Header = &header
	}

	fsKeys := reg.ListFileSpecs()
	sort.Strings(fsKeys)

	for _, fsKey := range fsKeys {
		if filterFileSpec != "" && fsKey != filterFileSpec {
			continue
		}

		fs := reg.FileSpecs()[fsKey]
		fsDoc := FileSpecDoc{
			Key:         fsKey,
			Program:     fs.Program,
			Section:     fs.Section,
			Description: fs.Description,
		}

		// Group validators — for message rendering, use the record_type param if it exists
		// (e.g. duplicate detection validators), otherwise use the filespec key as a fallback.
		for _, cv := range validators.GetGroupValidators(fsKey) {
			groupRecordType := fsKey
			if rt, ok := cv.Params["record_type"]; ok {
				if s, ok := rt.(string); ok {
					groupRecordType = s
				}
			}
			fsDoc.Group = append(fsDoc.Group, validatorToDoc(cv, groupRecordType, nil))
		}

		for _, schemaPath := range fs.Schemas {
			// Skip header (rendered once at top level) and trailer (never validated)
			if schemaPath == "common/header" || schemaPath == "common/trailer" {
				continue
			}
			cs := reg.GetSchema(schemaPath)
			if cs == nil {
				continue
			}
			if filterRecord != "" && cs.RecordType != filterRecord {
				continue
			}
			fsDoc.Records = append(fsDoc.Records, buildRecordDoc(cs, schemaPath, validators))
		}

		model.FileSpecs = append(model.FileSpecs, fsDoc)
	}

	return model
}

func buildRecordDoc(cs *schema.CompiledSchema, schemaPath string, validators *validation.ValidatorRegistry) RecordDoc {
	recDoc := RecordDoc{
		RecordType:  cs.RecordType,
		SchemaPath:  schemaPath,
		Description: cs.Description,
	}

	for _, cv := range validators.GetRecordValidators(schemaPath) {
		vDoc := validatorToDoc(cv, cs.RecordType, nil)
		if cv.ErrorType == validation.ErrorTypeRecordPreCheck {
			recDoc.PreCheck = append(recDoc.PreCheck, vDoc)
		} else {
			recDoc.CrossField = append(recDoc.CrossField, vDoc)
		}
	}

	for _, field := range cs.Shared {
		recDoc.Fields = append(recDoc.Fields, buildFieldDoc(field, cs.RecordType, schemaPath, validators))
	}

	if len(cs.Segments) > 0 {
		for _, field := range cs.Segments[0].Fields {
			recDoc.Fields = append(recDoc.Fields, buildFieldDoc(field, cs.RecordType, schemaPath, validators))
		}
	}

	return recDoc
}

func buildFieldDoc(field schema.FieldDef, recordType string, schemaPath string, validators *validation.ValidatorRegistry) FieldDoc {
	fDoc := FieldDoc{
		Name:         field.Name,
		Item:         field.Item,
		FriendlyName: field.FriendlyName,
		Type:         field.Type,
		Required:     field.Required,
	}

	// Deduplicate validators — multi-segment records (e.g. T3) register the same
	// validators once per segment, producing duplicates for the same field name.
	seen := make(map[string]bool)
	for _, cv := range validators.GetFieldValidators(schemaPath, field.Name) {
		key := cv.ID + "|" + cv.Expression
		if seen[key] {
			continue
		}
		seen[key] = true
		fDoc.Validators = append(fDoc.Validators, validatorToDoc(cv, recordType, &field))
	}

	return fDoc
}

// validatorToDoc converts a CompiledValidator to a ValidatorDoc with a rendered example message.
func validatorToDoc(cv *validation.CompiledValidator, recordType string, field *schema.FieldDef) ValidatorDoc {
	return ValidatorDoc{
		Description: cv.Description,
		ErrorType:   cv.ErrorType,
		Message:     renderMessage(cv, recordType, field),
		Fields:      cv.Fields,
	}
}

// --- HTML renderer ---

func renderHTML(model *DocModel) (string, error) {
	tmplData, err := templateFS.ReadFile("templates/validation-reference.html.tmpl")
	if err != nil {
		return "", fmt.Errorf("reading embedded template: %w", err)
	}

	tmpl, err := template.New("html").Funcs(htmlFuncMap()).Parse(string(tmplData))
	if err != nil {
		return "", fmt.Errorf("parsing HTML template: %w", err)
	}

	var b strings.Builder
	err = tmpl.Execute(&b, struct {
		Model *DocModel
	}{
		Model: model,
	})
	if err != nil {
		return "", fmt.Errorf("executing HTML template: %w", err)
	}

	return b.String(), nil
}

func htmlFuncMap() template.FuncMap {
	return template.FuncMap{
		"lower":   strings.ToLower,
		"replace": strings.ReplaceAll,
		"anchorID": func(s string) string {
			return strings.ToLower(strings.ReplaceAll(strings.ReplaceAll(s, ":", "-"), "/", "-"))
		},
		"yesNo": func(b bool) string {
			if b {
				return "Yes"
			}
			return "No"
		},
		"joinFields":    func(fields []string) string { return strings.Join(fields, ", ") },
		"friendlyError": friendlyErrorType,
		"hasValidators": func(f FieldDoc) bool { return len(f.Validators) > 0 },
		"hasFields":     func(v ValidatorDoc) bool { return len(v.Fields) > 0 },
	}
}
