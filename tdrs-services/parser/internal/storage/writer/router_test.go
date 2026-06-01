package writer

import (
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
)

func TestNewRouter_UsesPrefixedParserErrorTable(t *testing.T) {
	reg := config.NewTestRegistry(map[string]*schema.CompiledSchema{})
	spec := &filespec.FileSpec{
		Program: "TEST",
		Section: 1,
		Schemas: []string{},
	}

	router := NewRouter(&mockSink{}, 42, spec, reg, RouterConfig{
		IncludeErrors:       true,
		ErrorFlushThreshold: 100,
		TablePrefix:         config.DefaultTablePrefix,
	})

	if router.ErrorTableName() != "shadow_parser_error" {
		t.Errorf("ErrorTableName = %q, want shadow_parser_error", router.ErrorTableName())
	}
}
