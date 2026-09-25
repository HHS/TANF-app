package db

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
	"testing"
)

func TestGoParserDoesNotWriteProductionSubmissionState(t *testing.T) {
	_, sourceFile, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("could not locate Go parser source tree")
	}
	moduleRoot := filepath.Clean(filepath.Join(filepath.Dir(sourceFile), "..", ".."))
	stateWrite := regexp.MustCompile(`(?is)UPDATE\s+data_files_datafile\s+SET\s+state\b|func\s+UpdateDataFileState\b`)

	var violations []string
	err := filepath.WalkDir(moduleRoot, func(path string, entry os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if entry.IsDir() || filepath.Ext(path) != ".go" || strings.HasSuffix(path, "_test.go") {
			return nil
		}
		source, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		if stateWrite.Match(source) {
			relativePath, relErr := filepath.Rel(moduleRoot, path)
			if relErr != nil {
				return relErr
			}
			violations = append(violations, relativePath)
		}
		return nil
	})
	if err != nil {
		t.Fatalf("scan Go parser state writers: %v", err)
	}
	if len(violations) != 0 {
		t.Fatalf("Go parser must send production state outcomes to Python; found state writers in %v", violations)
	}
}

func TestDataFileHelpersRejectUnsupportedTables(t *testing.T) {
	ctx := context.Background()
	df := &DataFileRecord{ID: 42}

	tests := []struct {
		name string
		err  error
		want string
	}{
		{
			name: "get datafile",
			err:  func() error { _, err := GetDataFile(ctx, nil, "unknown_table", 42); return err }(),
			want: `unsupported datafile table "unknown_table"`,
		},
		{
			name: "ensure datafile",
			err:  EnsureShadowDataFile(ctx, nil, "unknown_table", df),
			want: `unsupported datafile table "unknown_table"`,
		},
		{
			name: "ensure summary",
			err:  EnsureDataFileSummary(ctx, nil, "unknown_summary", 42),
			want: `unsupported datafile summary table "unknown_summary"`,
		},
		{
			name: "update summary result",
			err:  UpdateDataFileSummaryResult(ctx, nil, "unknown_summary", 42, 1, 1),
			want: `unsupported datafile summary table "unknown_summary"`,
		},
		{
			name: "update summary status",
			err:  UpdateDataFileSummaryStatus(ctx, nil, "unknown_summary", 42, "Complete"),
			want: `unsupported datafile summary table "unknown_summary"`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.err == nil {
				t.Fatal("expected error, got nil")
			}
			if !strings.Contains(tt.err.Error(), tt.want) {
				t.Fatalf("error = %q, want to contain %q", tt.err.Error(), tt.want)
			}
		})
	}
}

func TestInt64ToInt4(t *testing.T) {
	got, err := int64ToInt4(42)
	if err != nil {
		t.Fatalf("int64ToInt4(42) unexpected error: %v", err)
	}
	if !got.Valid || got.Int32 != 42 {
		t.Fatalf("int64ToInt4(42) = %+v, want valid 42", got)
	}

	if _, err := int64ToInt4(-1); err == nil {
		t.Fatal("int64ToInt4(-1) error = nil, want error")
	}
	if _, err := int64ToInt4(1 << 40); err == nil {
		t.Fatal("int64ToInt4(1 << 40) error = nil, want error")
	}
}

func TestMarshalStateTransitionMetadataIncludesCorrelation(t *testing.T) {
	got, err := marshalStateTransitionMetadata(
		42,
		"parse_started",
		"parse_failed",
		DataFileStateTransitionContext{
			EventID:       "123e4567-e89b-12d3-a456-426614174000",
			Note:          "Go parser pipeline processing failed",
			Source:        "go_parser",
			TaskName:      "tdpservice.scheduling.parser_task.go_parse",
			CeleryTaskID:  "987e6543-e21b-12d3-a456-426614174000",
			ReparseMetaID: 7,
			Metadata: map[string]any{
				"stage": "pipeline",
			},
		},
	)
	if err != nil {
		t.Fatalf("marshalStateTransitionMetadata() error = %v", err)
	}

	var metadata map[string]any
	if err := json.Unmarshal(got, &metadata); err != nil {
		t.Fatalf("json.Unmarshal() error = %v", err)
	}

	if metadata["data_file_id"] != float64(42) {
		t.Errorf("data_file_id = %#v, want 42", metadata["data_file_id"])
	}
	if metadata["previous_state"] != "parse_started" {
		t.Errorf("previous_state = %#v", metadata["previous_state"])
	}
	if metadata["next_state"] != "parse_failed" {
		t.Errorf("next_state = %#v", metadata["next_state"])
	}
	if metadata["source"] != "go_parser" {
		t.Errorf("source = %#v", metadata["source"])
	}
	if metadata["event_id"] != "123e4567-e89b-12d3-a456-426614174000" {
		t.Errorf("event_id = %#v", metadata["event_id"])
	}
	if metadata["task_name"] != "tdpservice.scheduling.parser_task.go_parse" {
		t.Errorf("task_name = %#v", metadata["task_name"])
	}
	if metadata["celery_task_id"] != "987e6543-e21b-12d3-a456-426614174000" {
		t.Errorf("celery_task_id = %#v", metadata["celery_task_id"])
	}
	if metadata["reparse_meta_id"] != float64(7) {
		t.Errorf("reparse_meta_id = %#v", metadata["reparse_meta_id"])
	}
	if metadata["reparse_id"] != float64(7) {
		t.Errorf("reparse_id = %#v", metadata["reparse_id"])
	}
	if metadata["stage"] != "pipeline" {
		t.Errorf("stage = %#v", metadata["stage"])
	}
	if metadata["transition_path"] != "go_sql" {
		t.Errorf("transition_path = %#v", metadata["transition_path"])
	}
}

func TestResolveLogEventUUID(t *testing.T) {
	const eventID = "123e4567-e89b-12d3-a456-426614174000"

	got, err := resolveLogEventUUID(eventID)
	if err != nil {
		t.Fatalf("resolveLogEventUUID() error = %v", err)
	}
	if got.String() != eventID {
		t.Fatalf("resolveLogEventUUID() = %q, want %q", got.String(), eventID)
	}

	if _, err := resolveLogEventUUID("not-a-uuid"); err == nil {
		t.Fatal("resolveLogEventUUID() accepted an invalid UUID")
	}
}

func TestStateTransitionSQLTargetsAuditTable(t *testing.T) {
	if !strings.Contains(insertDataFileStateTransition, "core_baselog") {
		t.Fatalf("state transition insert does not create base log")
	}
	if !strings.Contains(insertDataFileStateTransition, "data_files_datafilestatetransition") {
		t.Fatalf("state transition insert does not create child transition")
	}
	if !strings.Contains(insertDataFileStateTransition, "baselog_ptr_id") {
		t.Fatalf("state transition insert does not use inherited parent link")
	}
}

func TestUpdateShadowDataFileStateRejectsProductionWrites(t *testing.T) {
	err := UpdateShadowDataFileState(context.Background(), nil, productionDataFileTable, 42, "parse_completed")
	if err == nil || !strings.Contains(err.Error(), "owned by the Django lifecycle controller") {
		t.Fatalf("expected production lifecycle protection, got %v", err)
	}
}
