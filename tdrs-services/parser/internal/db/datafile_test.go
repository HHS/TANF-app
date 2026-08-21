package db

import (
	"context"
	"strings"
	"testing"
)

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
			name: "update datafile state",
			err:  UpdateDataFileState(ctx, nil, "unknown_table", 42, "Parsing"),
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
