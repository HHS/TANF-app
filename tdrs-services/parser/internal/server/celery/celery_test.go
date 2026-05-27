package celery

import (
	"context"
	"go-parser/internal/config"
	"go-parser/internal/pipeline"
	"go-parser/internal/server"
	"strings"
	"testing"
)

func TestSectionNumber(t *testing.T) {
	tests := []struct {
		name    string
		section string
		want    int
	}{
		{"Active Case Data", "Active Case Data", 1},
		{"Closed Case Data", "Closed Case Data", 2},
		{"Aggregate Data", "Aggregate Data", 3},
		{"Stratum Data", "Stratum Data", 4},
		{"unknown section", "Not A Real Section", 0},
		{"empty string", "", 0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := sectionNumber(tt.section)
			if got != tt.want {
				t.Errorf("sectionNumber(%q) = %d, want %d", tt.section, got, tt.want)
			}
		})
	}
}

func TestRun_MissingRedisURL(t *testing.T) {
	cfg := config.DefaultConfig()
	cfg.Server.Celery.RedisURL = ""

	s := &Server{
		Base: server.NewBase(cfg, nil, nil),
	}

	err := s.Run(context.Background())
	if err == nil {
		t.Fatal("expected error for missing redis URL")
	}
	if !strings.Contains(err.Error(), "server.celery.redis_url") {
		t.Errorf("error = %q, should mention server.celery.redis_url", err.Error())
	}
}

func TestRecordTotalsForResult(t *testing.T) {
	result := &pipeline.ParsingResult{
		RecordCounts: map[string]int64{
			"shadow_search_indexes_tanf_t1": 5,
			"shadow_search_indexes_tanf_t2": 7,
			"parser_error":                  3,
		},
		ErrorCount: 3,
	}

	created, total := recordTotalsForResult(result)
	if created != 12 {
		t.Errorf("created = %d, want 12", created)
	}
	if total != 12 {
		t.Errorf("total = %d, want 15", total)
	}
}

func TestDataFileStateForParsingResult(t *testing.T) {
	tests := []struct {
		name   string
		result *pipeline.ParsingResult
		want   string
	}{
		{
			name:   "nil result fails",
			result: nil,
			want:   dataFileStateParseFailed,
		},
		{
			name:   "no parser errors completes",
			result: &pipeline.ParsingResult{ErrorCount: 0},
			want:   dataFileStateParseCompleted,
		},
		{
			name:   "parser errors mark parsed with errors",
			result: &pipeline.ParsingResult{ErrorCount: 1},
			want:   dataFileStateParsedWithErrors,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := dataFileStateForParsingResult(tt.result); got != tt.want {
				t.Errorf("dataFileStateForParsingResult() = %q, want %q", got, tt.want)
			}
		})
	}
}
