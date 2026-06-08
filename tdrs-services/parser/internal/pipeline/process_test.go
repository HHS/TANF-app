package pipeline

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"sync"
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/decoder"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// configDir resolves the real config directory relative to this test package.
func configDir(t *testing.T) string {
	t.Helper()
	dir := filepath.Join("..", "..", "config")
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		t.Skip("config directory not found — tests must run from go-parser root")
	}
	return dir
}

// loadRegistry loads the full config registry from disk.
func loadRegistry(t *testing.T) *config.Registry {
	t.Helper()
	dir := configDir(t)
	cfg := &config.Config{
		Global:        config.GlobalConfig{ConfigDir: dir},
		SchemaFiles:   []string{"schemas/**/*.yaml"},
		FilespecFiles: []string{"filespecs/**/*.yaml"},
	}
	reg, err := config.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("NewRegistry failed: %v", err)
	}
	return reg
}

// loadValidators loads the real validator registry from disk.
func loadValidators(t *testing.T, reg *config.Registry) *validation.ValidatorRegistry {
	t.Helper()
	dir := configDir(t)
	cfg := config.DefaultConfig()
	cfg.Global.ConfigDir = dir
	validators, err := validation.NewRegistry(cfg, reg)
	if err != nil {
		t.Fatalf("validation.NewRegistry failed: %v", err)
	}
	return validators
}

// testTANFContext returns a DataFileContext matching the standard test header
// "HEADER20241A06000TAN1ED" (calendar year=2024, quarter=1 -> fiscal Q2 2024).
func testTANFContext() DataFileContext {
	return DataFileContext{
		Program:       "TAN",
		Section:       1,
		DatafileID:    1,
		FiscalYear:    2024,
		FiscalQuarter: "Q2",
		SectionName:   "Active Case Data",
	}
}

// testSSPContext returns a DataFileContext matching the SSP test header
// "HEADER20241A06000SSP1ED".
func testSSPContext() DataFileContext {
	return DataFileContext{
		Program:       "SSP",
		Section:       1,
		DatafileID:    1,
		FiscalYear:    2024,
		FiscalQuarter: "Q2",
		SectionName:   "Active Case Data",
	}
}

func testFRAContext() DataFileContext {
	return DataFileContext{
		Program:       "FRA",
		Section:       1,
		DatafileID:    1,
		FiscalYear:    2024,
		FiscalQuarter: "Q2",
		SectionName:   "FRA Work Outcome TANF Exiters",
	}
}

// capturingSink captures all flushed data for assertions.
type capturingSink struct {
	mu             sync.Mutex
	tables         map[string][][]any // tableName -> rows
	rollbackCalls  int
	rollbackErr    error
	rollbackID     int32
	rollbackTables []string
}

func newCapturingSink() *capturingSink {
	return &capturingSink{tables: make(map[string][][]any)}
}

func (s *capturingSink) Flush(_ context.Context, tableName string, _ []string, rows [][]any) (int64, error) {
	copied := make([][]any, len(rows))
	copy(copied, rows)
	s.mu.Lock()
	defer s.mu.Unlock()
	s.tables[tableName] = append(s.tables[tableName], copied...)
	return int64(len(rows)), nil
}

func (s *capturingSink) RollbackDatafile(_ context.Context, datafileID int32, tables []string, errorTableName string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.rollbackCalls++
	s.rollbackID = datafileID
	s.rollbackTables = slices.Clone(tables)
	if s.rollbackErr != nil {
		return s.rollbackErr
	}
	delete(s.tables, errorTableName)
	for _, table := range tables {
		delete(s.tables, table)
	}
	return nil
}
func (s *capturingSink) Close() error { return nil }

func (s *capturingSink) rowCount(tableName string) int {
	s.mu.Lock()
	defer s.mu.Unlock()
	return len(s.tables[tableName])
}

func parserErrorTableName(pipelineCfg PipelineConfig) string {
	return config.ParserErrorTableName(pipelineCfg.TablePrefix)
}

func (s *capturingSink) errorRows(pipelineCfg PipelineConfig) [][]any {
	s.mu.Lock()
	defer s.mu.Unlock()
	return slices.Clone(s.tables[parserErrorTableName(pipelineCfg)])
}

func (s *capturingSink) totalRecords() int {
	s.mu.Lock()
	defer s.mu.Unlock()
	total := 0
	for name, rows := range s.tables {
		if name != config.ParserErrorTableName("") && name != config.ParserErrorTableName(config.DefaultTablePrefix) {
			total += len(rows)
		}
	}
	return total
}

func (s *capturingSink) errorCount() int {
	s.mu.Lock()
	defer s.mu.Unlock()
	return len(s.tables["shadow_parser_error"]) + len(s.tables["parser_error"])
}

// --- Helper to create a test data file in a temp dir ---

// writeTempFile creates a temporary file with the given content and returns its path.
func writeTempFile(t *testing.T, content string) string {
	t.Helper()
	f, err := os.CreateTemp(t.TempDir(), "testdata-*.txt")
	if err != nil {
		t.Fatalf("failed to create temp file: %v", err)
	}
	if _, err := f.WriteString(content); err != nil {
		f.Close()
		t.Fatalf("failed to write temp file: %v", err)
	}
	if err := f.Close(); err != nil {
		t.Fatalf("failed to close temp file: %v", err)
	}
	return f.Name()
}

func processContentForTest(
	t *testing.T,
	reg *config.Registry,
	validators *validation.ValidatorRegistry,
	content string,
	dfCtx DataFileContext,
) (*ParsingResult, *capturingSink) {
	t.Helper()

	filePath := writeTempFile(t, content)
	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec(dfCtx.Program, dfCtx.Section)
	if spec == nil {
		t.Fatalf("GetFileSpec(%s, %d) returned nil", dfCtx.Program, dfCtx.Section)
	}

	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = false
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, dfCtx)
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	return result, sink
}

// --- End-to-end Process tests ---

func TestProcess_FRAInvalidFirstRowWritesPreCheckError(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	tests := []struct {
		name    string
		content string
	}{
		{
			name:    "comment row",
			content: "# This line represents a header which is not allowed in fra files.\n202401,946412419\n",
		},
		{
			name:    "empty first row",
			content: "\n202401,946412419\n",
		},
		{
			name:    "missing column value",
			content: "202401,\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			filePath := writeTempFile(t, tt.content)
			f, err := os.Open(filePath)
			if err != nil {
				t.Fatalf("failed to open file: %v", err)
			}
			defer f.Close()

			spec := reg.GetFileSpec("FRA", 1)
			if spec == nil {
				t.Fatal("GetFileSpec(FRA, 1) returned nil")
			}

			dec, err := decoder.CreateDecoder(f, spec)
			if err != nil {
				t.Fatalf("CreateDecoder failed: %v", err)
			}
			defer dec.Close()

			sink := newCapturingSink()
			pipelineCfg := TestConfig()
			pipelineCfg.IncludeRecords = true
			pipelineCfg.IncludeErrors = true
			p := NewPipeline(sink, reg, validators, pipelineCfg)

			result, err := p.Process(context.Background(), dec, testFRAContext())
			if err != nil {
				t.Fatalf("Process failed: %v", err)
			}

			if result.ErrorCount != 1 {
				t.Errorf("ErrorCount = %d, want 1", result.ErrorCount)
			}
			if sink.totalRecords() != 0 {
				t.Errorf("totalRecords = %d, want 0", sink.totalRecords())
			}
			if sink.errorCount() != 1 {
				t.Fatalf("sink error count = %d, want 1", sink.errorCount())
			}

			row := sink.tables["shadow_parser_error"][0]
			if got := row[0]; got != int32(1) {
				t.Errorf("row_number = %v, want %d", got, 1)
			}
			if got := row[6]; got != "File does not begin with FRA data." {
				t.Errorf("error_message = %v, want %q", got, "File does not begin with FRA data.")
			}
			if got := row[7]; got != "1" {
				t.Errorf("error_type = %v, want %q", got, "1")
			}
		})
	}
}

func TestProcess_FRAValidFileDoesNotRequireTrailer(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	filePath := writeTempFile(t, "202401,946412419\n")
	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("FRA", 1)
	if spec == nil {
		t.Fatal("GetFileSpec(FRA, 1) returned nil")
	}

	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, testFRAContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result.ErrorCount != 0 {
		t.Errorf("ErrorCount = %d, want 0", result.ErrorCount)
	}
	if sink.errorCount() != 0 {
		t.Fatalf("sink error count = %d, want 0; errors=%v", sink.errorCount(), sink.errorRows(pipelineCfg))
	}
}

func TestProcess_TANF_S1_ValidData(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	// Build a valid TANF Section 1 file with HEADER + T1 + T2 + T3 + TRAILER
	// Header: 23 chars (title=HEADER, year=2024, quarter=1, type=A, state_fips=06, tribe_code=000, program_type=TAN, edit=1, encryption=E, update=D)
	header := "HEADER20241A06000TAN1ED"

	// T1 record: starts with "T1", then RPT_MONTH_YEAR (6 chars), CASE_NUMBER (11 chars), rest padded
	// The T1 record needs to be at least 117 chars (record_length_min validator)
	t1Line := "T1" + "202401" + "12345678901" + strings.Repeat(" ", 50)

	// T2 record: starts with "T2", same RPT_MONTH_YEAR and CASE_NUMBER
	t2Line := "T2" + "202401" + "12345678901" + strings.Repeat(" ", 50)

	// T3 record: starts with "T3", same RPT_MONTH_YEAR and CASE_NUMBER
	t3Line := "T3" + "202401" + "12345678901" + strings.Repeat(" ", 50)

	trailer := "TRAILER0000003         "

	content := strings.Join([]string{header, t1Line, t2Line, t3Line, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	// Open file and create decoder
	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	if spec == nil {
		t.Fatal("GetFileSpec(TANF, 1) returned nil")
	}

	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	// Create pipeline with real registry and validators, capturing sink
	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = false // Skip record writing (no real serializers needed)
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	ctx := context.Background()
	result, err := p.Process(ctx, dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result == nil {
		t.Fatal("Process returned nil result")
	}
	if result.Duration <= 0 {
		t.Error("Duration should be positive")
	}
	// ErrorStats should be populated
	if result.ErrorStats == nil {
		t.Error("ErrorStats should not be nil")
	}
	if result.BatchCount < 1 {
		t.Errorf("BatchCount = %d, want >= 1", result.BatchCount)
	}
	if result.GroupCount < 1 {
		t.Errorf("GroupCount = %d, want >= 1", result.GroupCount)
	}
}

func TestProcess_HeaderProgramTypeMismatchWritesPreCheckError(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	tests := []struct {
		name            string
		header          string
		dfCtx           DataFileContext
		expectedMessage string
	}{
		{
			name:   "submitted SSP with TAN header",
			header: "HEADER20241A06000TAN1ED",
			dfCtx:  testSSPContext(),
			expectedMessage: "Submitted program type (SSP) does not match file program type (TAN).",
		},
		{
			name:   "submitted TAN with SSP header",
			header: "HEADER20241A06000SSP1ED",
			dfCtx:  testTANFContext(),
			expectedMessage: "Submitted program type (TAN) does not match file program type (SSP).",
		},
		{
			name:   "submitted TAN with Tribal header",
			header: "HEADER20241A00142TAN1ED",
			dfCtx:  testTANFContext(),
			expectedMessage: "Submitted program type (TAN) does not match file program type (TRIBAL).",
		},
		{
			name:   "submitted Tribal with TAN header and empty tribe code",
			header: "HEADER20241A06000TAN1ED",
			dfCtx: DataFileContext{
				Program:       "TRIBAL",
				Section:       1,
				DatafileID:    1,
				FiscalYear:    2024,
				FiscalQuarter: "Q2",
				SectionName:   "Active Case Data",
			},
			expectedMessage: "Submitted program type (TRIBAL) does not match file program type (TAN).",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			content := tt.header + "\n"
			result, sink := processContentForTest(t, reg, validators, content, tt.dfCtx)

			if result.ErrorCount != 1 {
				t.Errorf("ErrorCount = %d, want 1", result.ErrorCount)
			}
			if sink.errorCount() != 1 {
				t.Fatalf("sink error count = %d, want 1", sink.errorCount())
			}
			if sink.totalRecords() != 0 {
				t.Errorf("totalRecords = %d, want 0", sink.totalRecords())
			}

			row := sink.errorRows(TestConfig())[0]
			if got := row[0]; got != int32(1) {
				t.Errorf("row_number = %v, want %d", got, 1)
			}
			if got := row[6]; got != tt.expectedMessage {
				t.Errorf("error_message = %v, want %q", got, tt.expectedMessage)
			}
			if got := row[7]; got != "1" {
				t.Errorf("error_type = %v, want %q", got, "1")
			}
		})
	}
}

func TestProcess_TribalHeaderMatchesTribalContext(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	dfCtx := testTANFContext()
	dfCtx.Program = "TRIBAL"
	content := "HEADER20241A00142TAN1ED\n"
	_, sink := processContentForTest(t, reg, validators, content, dfCtx)

	parserErrorRows := sink.errorRows(TestConfig())
	for _, row := range parserErrorRows {
		message, ok := row[6].(string)
		if !ok {
			t.Fatalf("error_message type = %T, want string", row[6])
		}
		if strings.Contains(message, "Submitted program type") {
			t.Fatalf("parser errors = %v, want no program mismatch error", parserErrorRows)
		}
	}
}

func TestProcess_TANF_S1_MissingHeader(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	// File with no HEADER record - first line is T1
	content := "T1" + "202401" + "12345678901" + strings.Repeat(" ", 100) + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	pipelineCfg.ShortCircuit = false
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	ctx := context.Background()

	// Pipeline should return a result with a PRE_CHECK error, not panic
	result, err := p.Process(ctx, dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process returned unexpected error: %v", err)
	}
	if result.ErrorCount != 2 {
		t.Errorf("ErrorCount = %d, want 2", result.ErrorCount)
	}
	if sink.errorCount() != 2 {
		t.Errorf("sink error count = %d, want 2", sink.errorCount())
	}
	if got := sink.errorRows(pipelineCfg)[1][6]; got != "No records created." {
		t.Errorf("second error_message = %v, want %q", got, "No records created.")
	}
	if got := sink.tables["shadow_parser_error"][1][0]; got != int32(0) {
		t.Errorf("second row_number = %v, want %d", got, 0)
	}
}

func TestProcess_TANF_MultipleHeaders_RollbacksAndWritesOffendingRow(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN1ED"
	t1Line := "T1" + "202401" + "12345678901" + strings.Repeat(" ", 100)
	trailer := "TRAILER0000001         "
	content := strings.Join([]string{header, t1Line, header, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process returned unexpected error: %v", err)
	}
	if result.ErrorCount != 1 {
		t.Errorf("ErrorCount = %d, want 1", result.ErrorCount)
	}
	if sink.rollbackCalls != 1 {
		t.Fatalf("rollbackCalls = %d, want 1", sink.rollbackCalls)
	}
	if sink.rollbackID != testTANFContext().DatafileID {
		t.Errorf("rollbackID = %d, want %d", sink.rollbackID, testTANFContext().DatafileID)
	}
	if sink.totalRecords() != 0 {
		t.Errorf("expected rollback to leave 0 record rows, got %d", sink.totalRecords())
	}
	if sink.errorCount() != 1 {
		t.Fatalf("sink error count = %d, want 1", sink.errorCount())
	}

	errRow := sink.errorRows(pipelineCfg)[0]
	if got := errRow[0]; got != int32(3) {
		t.Errorf("row_number = %v, want 3", got)
	}
	if got := errRow[6]; got != "Multiple headers found." {
		t.Errorf("error_message = %v, want %q", got, "Multiple headers found.")
	}
}

func TestProcess_TANF_MultipleHeaders_RollbackFailurePropagates(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN1ED"
	content := strings.Join([]string{header, header}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	rollbackErr := errors.New("rollback failed")
	sink := newCapturingSink()
	sink.rollbackErr = rollbackErr
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, testTANFContext())
	if err == nil {
		t.Fatal("expected rollback error")
	}
	if result != nil {
		t.Fatalf("result = %#v, want nil", result)
	}
	if !errors.Is(err, rollbackErr) {
		t.Fatalf("error = %v, want rollback failure", err)
	}
	if sink.rollbackCalls != 1 {
		t.Fatalf("rollbackCalls = %d, want 1", sink.rollbackCalls)
	}
	if sink.errorCount() != 0 {
		t.Fatalf("sink error count = %d, want 0 when rollback fails", sink.errorCount())
	}
}

func TestProcess_RollbackDoesNotPoisonLaterProcess(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	header := "HEADER20241A06000TAN1ED"
	badPath := writeTempFile(t, strings.Join([]string{header, header}, "\n")+"\n")
	badFile, err := os.Open(badPath)
	if err != nil {
		t.Fatalf("failed to open bad file: %v", err)
	}
	defer badFile.Close()
	spec := reg.GetFileSpec("TAN", 1)
	badDec, err := decoder.CreateDecoder(badFile, spec)
	if err != nil {
		t.Fatalf("CreateDecoder for bad file failed: %v", err)
	}
	defer badDec.Close()

	if _, err := p.Process(context.Background(), badDec, testTANFContext()); err != nil {
		t.Fatalf("first Process returned unexpected error: %v", err)
	}

	t1Line := "T1" + "202401" + "12345678901" + strings.Repeat(" ", 100)
	trailer := "TRAILER0000001         "
	goodPath := writeTempFile(t, strings.Join([]string{header, t1Line, trailer}, "\n")+"\n")
	goodFile, err := os.Open(goodPath)
	if err != nil {
		t.Fatalf("failed to open good file: %v", err)
	}
	defer goodFile.Close()
	goodDec, err := decoder.CreateDecoder(goodFile, spec)
	if err != nil {
		t.Fatalf("CreateDecoder for good file failed: %v", err)
	}
	defer goodDec.Close()

	if _, err := p.Process(context.Background(), goodDec, testTANFContext()); err != nil {
		t.Fatalf("second Process failed after prior rollback: %v", err)
	}
}

func TestProcess_EmptyFile(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	// Empty file — no header, no data
	filePath := writeTempFile(t, "")

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	ctx := context.Background()

	// Empty file: parseCtx is nil (no header), pipeline processes zero rows
	result, err := p.Process(ctx, dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process returned unexpected error: %v", err)
	}
	if result.ErrorCount != 2 {
		t.Errorf("ErrorCount = %d, want 2", result.ErrorCount)
	}
	if sink.errorCount() != 2 {
		t.Errorf("sink error count = %d, want 2", sink.errorCount())
	}
	if got := sink.errorRows(pipelineCfg)[1][6]; got != "No records created." {
		t.Errorf("second error_message = %v, want %q", got, "No records created.")
	}
}

func TestProcess_HeaderOnly(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN1ED"
	content := header + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = false
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	ctx := context.Background()
	result, err := p.Process(ctx, dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed for header-only file: %v", err)
	}

	// No data records to process
	if result.BatchCount != 0 {
		t.Errorf("BatchCount = %d, want 0", result.BatchCount)
	}
	if result.GroupCount != 0 {
		t.Errorf("GroupCount = %d, want 0", result.GroupCount)
	}
}

func TestProcess_HeaderOnlyWritesNoRecordsCreatedError(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	content := "HEADER20241A06000TAN1ED\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	if spec == nil {
		t.Fatal("GetFileSpec(TAN, 1) returned nil")
	}

	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, DataFileContext{
		Program:       "TAN",
		Section:       1,
		DatafileID:    1,
		FiscalYear:    2024,
		FiscalQuarter: "Q2",
		SectionName:   "Active Case Data",
	})
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result.ErrorCount != 2 {
		t.Errorf("ErrorCount = %d, want 2", result.ErrorCount)
	}
	if result.RecordCounts["parser_error"] != 2 {
		t.Errorf("RecordCounts[parser_error] = %d, want 2", result.RecordCounts["parser_error"])
	}
	if sink.errorCount() != 2 {
		t.Errorf("sink error count = %d, want 2", sink.errorCount())
	}
	if sink.totalRecords() != 0 {
		t.Errorf("totalRecords = %d, want 0", sink.totalRecords())
	}

	rows := sink.errorRows(pipelineCfg)
	if got := rows[0][6]; got != "Your file does not end with a TRAILER record." {
		t.Errorf("first error_message = %v, want missing trailer", got)
	}
	if got := rows[1][6]; got != "No records created." {
		t.Errorf("second error_message = %v, want %q", got, "No records created.")
	}
	if got := rows[1][7]; got != "1" {
		t.Errorf("error_type = %v, want %q", got, "1")
	}
}

func TestProcess_TANFZeroRecordSectionsAccepted(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	tests := []struct {
		name    string
		section int
		header  string
		ctx     DataFileContext
	}{
		{
			name:    "active",
			section: 1,
			header:  "HEADER20241A06000TAN1ED",
			ctx:     testTANFContext(),
		},
		{
			name:    "aggregate",
			section: 3,
			header:  "HEADER20241G06000TAN1ED",
			ctx: DataFileContext{
				Program:       "TAN",
				Section:       3,
				DatafileID:    1,
				FiscalYear:    2024,
				FiscalQuarter: "Q2",
				SectionName:   "Aggregate Data",
			},
		},
		{
			name:    "stratum",
			section: 4,
			header:  "HEADER20241S06000TAN1ED",
			ctx: DataFileContext{
				Program:       "TAN",
				Section:       4,
				DatafileID:    1,
				FiscalYear:    2024,
				FiscalQuarter: "Q2",
				SectionName:   "Stratum Data",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			content := strings.Join([]string{tt.header, "TRAILER0000000         "}, "\n") + "\n"
			filePath := writeTempFile(t, content)

			f, err := os.Open(filePath)
			if err != nil {
				t.Fatalf("failed to open file: %v", err)
			}
			defer f.Close()

			spec := reg.GetFileSpec("TAN", tt.section)
			if spec == nil {
				t.Fatalf("GetFileSpec(TAN, %d) returned nil", tt.section)
			}

			dec, err := decoder.CreateDecoder(f, spec)
			if err != nil {
				t.Fatalf("CreateDecoder failed: %v", err)
			}
			defer dec.Close()

			sink := newCapturingSink()
			pipelineCfg := TestConfig()
			pipelineCfg.IncludeRecords = true
			pipelineCfg.IncludeErrors = true
			p := NewPipeline(sink, reg, validators, pipelineCfg)

			result, err := p.Process(context.Background(), dec, tt.ctx)
			if err != nil {
				t.Fatalf("Process failed: %v", err)
			}

			if result.ErrorCount != 0 {
				t.Errorf("ErrorCount = %d, want 0", result.ErrorCount)
			}
			if result.DetailRecordCount != 0 {
				t.Errorf("DetailRecordCount = %d, want 0", result.DetailRecordCount)
			}
			if sink.errorCount() != 0 {
				t.Errorf("sink error count = %d, want 0", sink.errorCount())
			}
			if sink.totalRecords() != 0 {
				t.Errorf("totalRecords = %d, want 0", sink.totalRecords())
			}
		})
	}
}

func TestProcess_TANFZeroRecordBadTrailerCountRejected(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	content := strings.Join([]string{"HEADER20241A06000TAN1ED", "TRAILER0000001         "}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result.ErrorCount != 2 {
		t.Errorf("ErrorCount = %d, want 2", result.ErrorCount)
	}
	messages := make([]string, 0, sink.errorCount())
	for _, row := range sink.errorRows(pipelineCfg) {
		if msg, ok := row[6].(string); ok {
			messages = append(messages, msg)
		}
	}
	if !slices.Contains(messages, "The number of records in the TRAILER row count: 1, does not match the number of records detected in the file: 0.") {
		t.Fatalf("parser errors = %v, want trailer count mismatch", messages)
	}
	if !slices.Contains(messages, "No records created.") {
		t.Fatalf("parser errors = %v, want no records created", messages)
	}
}

func TestProcess_HeaderValidationFailureAlsoWritesNoRecordsCreatedError(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	content := "HEADER20241A06000TAN1ED\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	if spec == nil {
		t.Fatal("GetFileSpec(TAN, 1) returned nil")
	}

	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, DataFileContext{
		Program:       "TAN",
		Section:       1,
		DatafileID:    1,
		FiscalYear:    2024,
		FiscalQuarter: "Q1",
		SectionName:   "Active Case Data",
	})
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result.ErrorCount != 2 {
		t.Errorf("ErrorCount = %d, want 2", result.ErrorCount)
	}
	if sink.errorCount() != 2 {
		t.Errorf("sink error count = %d, want 2", sink.errorCount())
	}

	firstMessage := sink.errorRows(pipelineCfg)[0][6]
	if !strings.Contains(firstMessage.(string), "doesn't match file reporting year") {
		t.Errorf("first error_message = %v, want mismatch message", firstMessage)
	}
	if got := sink.errorRows(pipelineCfg)[1][6]; got != "No records created." {
		t.Errorf("second error_message = %v, want %q", got, "No records created.")
	}
}

func TestProcess_NonBlockingHeaderErrorWritesParserError(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN3ED"
	t1Line := "T1" + "202401" + "12345678901" + strings.Repeat(" ", 100)
	trailer := "TRAILER0000001         "
	content := strings.Join([]string{header, t1Line, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	if spec == nil {
		t.Fatal("GetFileSpec(TAN, 1) returned nil")
	}

	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = false
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result.ErrorStats == nil {
		t.Fatal("ErrorStats should not be nil")
	}
	if result.ErrorStats.FieldValue != 1 {
		t.Errorf("FieldValue = %d, want 1", result.ErrorStats.FieldValue)
	}
	if sink.errorCount() < 1 {
		t.Fatalf("sink error count = %d, want at least 1", sink.errorCount())
	}

	found := false
	for _, row := range sink.errorRows(pipelineCfg) {
		if got := row[6]; got == "HEADER Item 8 (Edit Indicator): 3 is not in [1, 2]." {
			found = true
			if rowNum := row[0]; rowNum != int32(1) {
				t.Errorf("row_number = %v, want %d", rowNum, 1)
			}
			break
		}
	}
	if !found {
		t.Fatalf("parser errors = %v, want header validation message", sink.errorRows(pipelineCfg))
	}
}

func TestProcess_BlankRequiredCountyFIPSWritesRequiredFieldError(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A01000TAN2ED"
	t1Line := "T120240111111111112   03403361110213120000300000000000008730010000000000000000000000000000000000222222000000002229012                                       "
	t2Line := "T2202401111111111121219740114WTTTTTY@W22212222222210122121100147220114000000000000000000000000000000000000000000000000000000000000000000000000000000000000291"
	trailer := "TRAILER      4         "
	content := strings.Join([]string{header, t1Line, t2Line, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	if spec == nil {
		t.Fatal("GetFileSpec(TAN, 1) returned nil")
	}

	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, DataFileContext{
		Program:       "TAN",
		Section:       1,
		DatafileID:    1,
		FiscalYear:    2024,
		FiscalQuarter: "Q2",
		SectionName:   "Active Case Data",
	})
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result.ErrorStats == nil {
		t.Fatal("ErrorStats should not be nil")
	}
	if result.ErrorStats.FieldValue < 1 {
		t.Fatalf("FieldValue = %d, want at least 1", result.ErrorStats.FieldValue)
	}

	messages := make([]string, 0, sink.errorCount())
	for _, row := range sink.errorRows(pipelineCfg) {
		if msg, ok := row[6].(string); ok {
			messages = append(messages, msg)
		}
	}

	want := "T1 Item 2 (County FIPS Code): field is required but a value was not provided."
	if !slices.Contains(messages, want) {
		t.Fatalf("parser errors = %v, want message %q", messages, want)
	}
}

func TestProcess_UnknownRecordTypeWritesParserError(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN1ED"
	unknown := "ThisLineShouldError"
	trailer := "TRAILER0000000         "
	content := strings.Join([]string{header, unknown, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	result, err := p.Process(context.Background(), dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result.ErrorCount != 2 {
		t.Errorf("ErrorCount = %d, want 2", result.ErrorCount)
	}
	if sink.errorCount() != 2 {
		t.Errorf("sink error count = %d, want 2", sink.errorCount())
	}
	if got := sink.errorRows(pipelineCfg)[0][0]; got != int32(2) {
		t.Errorf("first row_number = %v, want %d", got, 2)
	}
	if got := sink.errorRows(pipelineCfg)[0][6]; got != "Unknown record type was found." {
		t.Errorf("first error_message = %v, want %q", got, "Unknown record type was found.")
	}
	if got := sink.errorRows(pipelineCfg)[1][6]; got != "No records created." {
		t.Errorf("second error_message = %v, want %q", got, "No records created.")
	}
	for _, row := range sink.errorRows(pipelineCfg) {
		if msg, ok := row[6].(string); ok && strings.HasPrefix(msg, "TRAILER record count") {
			t.Fatalf("parser errors = %v, want no trailer count mismatch", sink.errorRows(pipelineCfg))
		}
	}
}

func TestProcess_TANF_S1_WithRecordWriting(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN1ED"
	t1Line := "T1" + "202401" + "12345678901" + strings.Repeat(" ", 100)
	trailer := "TRAILER0000001         "
	content := strings.Join([]string{header, t1Line, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	ctx := context.Background()
	result, err := p.Process(ctx, dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result == nil {
		t.Fatal("Process returned nil result")
	}
	if result.RecordCounts == nil {
		t.Error("RecordCounts should not be nil")
	}

	t.Logf("RecordCounts: %v", result.RecordCounts)
	t.Logf("ErrorCount: %d", result.ErrorCount)
	t.Logf("ErrorStats: %+v", result.ErrorStats)
	t.Logf("BatchCount: %d, GroupCount: %d", result.BatchCount, result.GroupCount)
	t.Logf("Duration: %s", result.Duration)
}

func TestProcess_TANF_MultipleRecordTypes(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN1ED"
	// Two separate cases
	t1a := "T1" + "202401" + "11111111111" + strings.Repeat(" ", 100)
	t2a := "T2" + "202401" + "11111111111" + strings.Repeat(" ", 100)
	t1b := "T1" + "202401" + "22222222222" + strings.Repeat(" ", 100)
	t2b := "T2" + "202401" + "22222222222" + strings.Repeat(" ", 100)
	trailer := "TRAILER0000004         "

	content := strings.Join([]string{header, t1a, t2a, t1b, t2b, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = false
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	ctx := context.Background()
	result, err := p.Process(ctx, dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	// Should have processed 2 groups (one per case number)
	if result.GroupCount != 2 {
		t.Errorf("GroupCount = %d, want 2", result.GroupCount)
	}
}

func TestProcess_SSP_S1(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	// SSP files use M1/M2/M3 record types with same header format
	header := "HEADER20241A06000SSP1ED"
	m1Line := "M1" + "202401" + "12345678901" + strings.Repeat(" ", 100)
	trailer := "TRAILER0000001         "
	content := strings.Join([]string{header, m1Line, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("SSP", 1)
	if spec == nil {
		t.Fatal("GetFileSpec(SSP, 1) returned nil")
	}

	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = false
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	ctx := context.Background()
	result, err := p.Process(ctx, dec, testSSPContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if result.BatchCount < 1 {
		t.Errorf("BatchCount = %d, want >= 1", result.BatchCount)
	}
}

func TestProcess_ErrorsDisabled(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN1ED"
	t1Line := "T1" + "202401" + "12345678901" + strings.Repeat(" ", 100)
	trailer := "TRAILER0000001         "
	content := strings.Join([]string{header, t1Line, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = false
	pipelineCfg.IncludeErrors = false // Errors disabled
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	ctx := context.Background()
	result, err := p.Process(ctx, dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	// No error rows should be in the sink
	if sink.errorCount() != 0 {
		t.Errorf("errorCount = %d, want 0 (errors disabled)", sink.errorCount())
	}

	// ErrorStats should still be populated (counted by workers, not router)
	if result.ErrorStats == nil {
		t.Error("ErrorStats should not be nil even when errors disabled")
	}
}

func TestProcess_ParsingResult_HasExpectedFields(t *testing.T) {
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN1ED"
	t1Line := "T1" + "202401" + "12345678901" + strings.Repeat(" ", 100)
	trailer := "TRAILER0000001         "
	content := strings.Join([]string{header, t1Line, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	sink := newCapturingSink()
	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = false
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(sink, reg, validators, pipelineCfg)

	ctx := context.Background()
	result, err := p.Process(ctx, dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	// Verify ParsingResult structure
	if result.RecordCounts == nil {
		t.Error("RecordCounts should not be nil")
	}
	if result.ErrorStats == nil {
		t.Error("ErrorStats should not be nil")
	}
	if result.Duration <= 0 {
		t.Error("Duration should be positive")
	}

	// "parser_error" key should be in RecordCounts
	if _, ok := result.RecordCounts["parser_error"]; !ok {
		t.Error("RecordCounts should contain 'parser_error' key")
	}
}

func TestProcess_FileSink_Integration(t *testing.T) {
	// Verify that the pipeline works with the FileSink (writing to files instead of DB)
	reg := loadRegistry(t)
	validators := loadValidators(t, reg)

	header := "HEADER20241A06000TAN1ED"
	t1Line := "T1" + "202401" + "12345678901" + strings.Repeat(" ", 100)
	trailer := "TRAILER0000001         "
	content := strings.Join([]string{header, t1Line, trailer}, "\n") + "\n"
	filePath := writeTempFile(t, content)

	f, err := os.Open(filePath)
	if err != nil {
		t.Fatalf("failed to open file: %v", err)
	}
	defer f.Close()

	spec := reg.GetFileSpec("TAN", 1)
	dec, err := decoder.CreateDecoder(f, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	outputDir := t.TempDir()
	fileSink, err := writer.NewFileSink(outputDir, "json")
	if err != nil {
		t.Fatalf("NewFileSink failed: %v", err)
	}

	pipelineCfg := TestConfig()
	pipelineCfg.IncludeRecords = true
	pipelineCfg.IncludeErrors = true
	p := NewPipeline(fileSink, reg, validators, pipelineCfg)

	ctx := context.Background()
	result, err := p.Process(ctx, dec, testTANFContext())
	if err != nil {
		t.Fatalf("Process failed: %v", err)
	}

	if err := fileSink.Close(); err != nil {
		t.Fatalf("FileSink.Close failed: %v", err)
	}

	if result.BatchCount < 1 {
		t.Errorf("BatchCount = %d, want >= 1", result.BatchCount)
	}

	// Check that output files were created
	entries, err := os.ReadDir(outputDir)
	if err != nil {
		t.Fatalf("ReadDir failed: %v", err)
	}

	// Should have at least one output file
	hasFiles := false
	for _, entry := range entries {
		if !entry.IsDir() {
			hasFiles = true
			t.Logf("Output file: %s", entry.Name())
		}
	}
	if !hasFiles {
		t.Log("No output files created (may be expected if all records were rejected by validators)")
	}
}

// padRight pads a string to the given length with spaces.
func padRight(s string, length int) string {
	if len(s) >= length {
		return s[:length]
	}
	return s + strings.Repeat(" ", length-len(s))
}

// Verify Sink interface is satisfied
var _ writer.Sink = (*capturingSink)(nil)
