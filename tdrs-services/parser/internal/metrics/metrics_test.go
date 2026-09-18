package metrics

import (
	"context"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func TestRegistryExportsPrometheusText(t *testing.T) {
	registry := NewRegistry("celery")
	UseDefault(registry)
	defer ResetDefault()

	RecordFileProcessed("TAN", 1, "success")
	ObserveFileDuration("TAN", 1, "success", 2*time.Second)
	AddRecordsParsed("TAN", 1, 12)
	AddErrorsGenerated("TAN", 1, "field_value", 3)
	ObservePipelineStage("TAN", 1, "parsing", 250*time.Millisecond)
	SetWorkerPoolCapacity("TAN", 1, 4)
	AddWorkerPoolActiveDuration("TAN", 1, 500*time.Millisecond)
	AddWorkerPoolCapacityDuration("TAN", 1, 250*time.Millisecond, 4)
	RecordFlush("search_indexes_tanf_t1", "success", 10*time.Millisecond)

	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rec := httptest.NewRecorder()
	registry.ServeHTTP(rec, req)

	body := rec.Body.String()
	assertContains(t, body, "# TYPE go_parser_files_processed_total counter")
	assertContains(t, body, `go_parser_files_processed_total{program="TAN",section="1",server_mode="celery",status="success"} 1`)
	assertContains(t, body, `go_parser_file_duration_seconds_count{program="TAN",section="1",server_mode="celery",status="success"} 1`)
	assertContains(t, body, `go_parser_records_parsed_total{program="TAN",section="1",server_mode="celery"} 12`)
	assertContains(t, body, `go_parser_errors_generated_total{error_category="field_value",program="TAN",section="1",server_mode="celery"} 3`)
	assertContains(t, body, `go_parser_worker_pool_configured_workers{program="TAN",section="1",server_mode="celery"} 4`)
	assertContains(t, body, `go_parser_worker_pool_active_duration_seconds_total{program="TAN",section="1",server_mode="celery"} 0.5`)
	assertContains(t, body, `go_parser_worker_pool_capacity_seconds_total{program="TAN",section="1",server_mode="celery"} 1`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="parsing"} 1`)
	assertContains(t, body, `go_parser_flushes_total{server_mode="celery",status="success",table="search_indexes_tanf_t1"} 1`)
	assertContains(t, body, `go_parser_flush_duration_seconds_count{server_mode="celery",status="success",table="search_indexes_tanf_t1"} 1`)
}

func TestInitializeParserMetricsExportsZeroSeries(t *testing.T) {
	registry := NewRegistry("celery")
	UseDefault(registry)
	defer ResetDefault()

	InitializeParserMetrics("TAN", 1)

	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rec := httptest.NewRecorder()
	registry.ServeHTTP(rec, req)

	body := rec.Body.String()
	assertContains(t, body, `go_parser_records_parsed_total{program="TAN",section="1",server_mode="celery"} 0`)
	assertContains(t, body, `go_parser_files_processed_total{program="TAN",section="1",server_mode="celery",status="success"} 0`)
	assertContains(t, body, `go_parser_files_processed_total{program="TAN",section="1",server_mode="celery",status="failed"} 0`)
	assertContains(t, body, `go_parser_errors_generated_total{error_category="record_pre_check",program="TAN",section="1",server_mode="celery"} 0`)
	assertContains(t, body, `go_parser_errors_generated_total{error_category="field_value",program="TAN",section="1",server_mode="celery"} 0`)
	assertContains(t, body, `go_parser_errors_generated_total{error_category="value_consistency",program="TAN",section="1",server_mode="celery"} 0`)
	assertContains(t, body, `go_parser_errors_generated_total{error_category="case_consistency",program="TAN",section="1",server_mode="celery"} 0`)
	assertContains(t, body, `go_parser_worker_pool_configured_workers{program="TAN",section="1",server_mode="celery"} 0`)
	assertContains(t, body, `go_parser_worker_pool_active_duration_seconds_total{program="TAN",section="1",server_mode="celery"} 0`)
	assertContains(t, body, `go_parser_worker_pool_capacity_seconds_total{program="TAN",section="1",server_mode="celery"} 0`)
	assertContains(t, body, `go_parser_file_duration_seconds_count{program="TAN",section="1",server_mode="celery",status="success"} 0`)
	assertContains(t, body, `go_parser_file_duration_seconds_sum{program="TAN",section="1",server_mode="celery",status="success"} 0`)
	assertContains(t, body, `go_parser_file_duration_seconds_bucket{le="+Inf",program="TAN",section="1",server_mode="celery",status="success"} 0`)
	assertContains(t, body, `go_parser_file_duration_seconds_count{program="TAN",section="1",server_mode="celery",status="failed"} 0`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="setup"} 0`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="parse_validate"} 0`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="flush"} 0`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_parsing"} 0`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_group_validation"} 0`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_record_validation"} 0`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_field_validation"} 0`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_routing"} 0`)
}

func TestInitializedParserMetricsIncrementFromZero(t *testing.T) {
	registry := NewRegistry("celery")
	UseDefault(registry)
	defer ResetDefault()

	InitializeParserMetrics("TAN", 1)
	AddRecordsParsed("TAN", 1, 12)
	AddErrorsGenerated("TAN", 1, "field_value", 3)
	RecordFileProcessed("TAN", 1, "success")
	ObserveFileDuration("TAN", 1, "success", 2*time.Second)
	ObservePipelineStage("TAN", 1, "setup", 250*time.Millisecond)
	AddWorkerPoolActiveDuration("TAN", 1, 500*time.Millisecond)
	AddWorkerPoolCapacityDuration("TAN", 1, 250*time.Millisecond, 4)

	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rec := httptest.NewRecorder()
	registry.ServeHTTP(rec, req)

	body := rec.Body.String()
	assertContains(t, body, `go_parser_records_parsed_total{program="TAN",section="1",server_mode="celery"} 12`)
	assertContains(t, body, `go_parser_errors_generated_total{error_category="field_value",program="TAN",section="1",server_mode="celery"} 3`)
	assertContains(t, body, `go_parser_files_processed_total{program="TAN",section="1",server_mode="celery",status="success"} 1`)
	assertContains(t, body, `go_parser_file_duration_seconds_count{program="TAN",section="1",server_mode="celery",status="success"} 1`)
	assertContains(t, body, `go_parser_file_duration_seconds_sum{program="TAN",section="1",server_mode="celery",status="success"} 2`)
	assertContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="setup"} 1`)
	assertContains(t, body, `go_parser_worker_pool_active_duration_seconds_total{program="TAN",section="1",server_mode="celery"} 0.5`)
	assertContains(t, body, `go_parser_worker_pool_capacity_seconds_total{program="TAN",section="1",server_mode="celery"} 1`)
}

func TestInitializeWriterMetricsExportsZeroSeries(t *testing.T) {
	registry := NewRegistry("celery")
	UseDefault(registry)
	defer ResetDefault()

	InitializeWriterMetrics("shadow_parser_error")

	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rec := httptest.NewRecorder()
	registry.ServeHTTP(rec, req)

	body := rec.Body.String()
	assertContains(t, body, `go_parser_flushes_total{server_mode="celery",status="success",table="shadow_parser_error"} 0`)
	assertContains(t, body, `go_parser_flushes_total{server_mode="celery",status="failed",table="shadow_parser_error"} 0`)
	assertContains(t, body, `go_parser_flush_duration_seconds_count{server_mode="celery",status="success",table="shadow_parser_error"} 0`)
	assertContains(t, body, `go_parser_flush_duration_seconds_sum{server_mode="celery",status="success",table="shadow_parser_error"} 0`)
	assertContains(t, body, `go_parser_flush_duration_seconds_bucket{le="+Inf",server_mode="celery",status="success",table="shadow_parser_error"} 0`)
}

func TestStartServerExposesMetricsEndpoint(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	server, err := StartMetricServer(ctx, MetricServerConfig{
		ServerMode:    "celery",
		ListenAddress: "127.0.0.1:0",
		Path:          "/metrics",
	})
	if err != nil {
		t.Fatalf("StartServer failed: %v", err)
	}
	defer server.Shutdown(context.Background())

	RecordFileProcessed("FRA", 1, "failed")

	resp, err := http.Get("http://" + server.Address() + "/metrics")
	if err != nil {
		t.Fatalf("GET /metrics failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status = %d, want 200", resp.StatusCode)
	}
	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("ReadAll failed: %v", err)
	}
	assertContains(t, string(bodyBytes), `go_parser_files_processed_total{program="FRA",section="1",server_mode="celery",status="failed"} 1`)
}

func TestStartServerExposesLocalServerModeMetrics(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	server, err := StartMetricServer(ctx, MetricServerConfig{
		ServerMode:    "local",
		ListenAddress: "127.0.0.1:0",
		Path:          "/metrics",
	})
	if err != nil {
		t.Fatalf("StartServer failed: %v", err)
	}
	defer server.Shutdown(context.Background())

	RecordFileProcessed("TAN", 1, "success")

	resp, err := http.Get("http://" + server.Address() + "/metrics")
	if err != nil {
		t.Fatalf("GET /metrics failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status = %d, want 200", resp.StatusCode)
	}
	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("ReadAll failed: %v", err)
	}
	assertContains(t, string(bodyBytes), `go_parser_files_processed_total{program="TAN",section="1",server_mode="local",status="success"} 1`)
}

func TestStartServerRejectsRelativePath(t *testing.T) {
	_, err := StartMetricServer(context.Background(), MetricServerConfig{
		ServerMode:    "celery",
		ListenAddress: "127.0.0.1:0",
		Path:          "metrics",
	})
	if err == nil {
		t.Fatal("expected error for relative metrics path")
	}
}

func assertContains(t *testing.T, body string, want string) {
	t.Helper()
	if !strings.Contains(body, want) {
		t.Fatalf("metrics body missing %q\nbody:\n%s", want, body)
	}
}
