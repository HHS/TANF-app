package celery

import (
	"context"
	"fmt"
	"go-parser/internal/config"
	"go-parser/internal/pipeline"
	"go-parser/internal/server"
	"strings"
	"testing"

	"github.com/gocelery/gocelery"
)

type fakeTaskSender struct {
	calls []fakeTaskCall
	err   error
}

type fakeTaskCall struct {
	task string
	args []interface{}
}

type fakeCeleryBroker struct {
	message *gocelery.TaskMessage
	err     error
}

func (f *fakeCeleryBroker) SendCeleryMessage(*gocelery.CeleryMessage) error {
	return nil
}

func (f *fakeCeleryBroker) GetTaskMessage() (*gocelery.TaskMessage, error) {
	return f.message, f.err
}

func (f *fakeTaskSender) Delay(task string, args ...interface{}) (*gocelery.AsyncResult, error) {
	f.calls = append(f.calls, fakeTaskCall{task: task, args: args})
	return nil, f.err
}

func TestCeleryTaskIDBrokerAddsEnvelopeIDToTaskArgs(t *testing.T) {
	const taskID = "987e6543-e21b-12d3-a456-426614174000"
	message := &gocelery.TaskMessage{
		ID:   taskID,
		Args: []interface{}{float64(42), float64(7), "event-id"},
	}
	broker := &celeryTaskIDBroker{
		CeleryBroker: &fakeCeleryBroker{message: message},
	}

	got, err := broker.GetTaskMessage()
	if err != nil {
		t.Fatalf("GetTaskMessage() error = %v", err)
	}
	if len(got.Args) != 4 {
		t.Fatalf("len(Args) = %d, want 4", len(got.Args))
	}
	if got.Args[3] != taskID {
		t.Errorf("Celery task ID arg = %#v, want %q", got.Args[3], taskID)
	}
}

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
		DetailRecordCount: 15,
		ErrorCount:        3,
	}

	created, total := recordTotalsForResult(result)
	if created != 12 {
		t.Errorf("created = %d, want 12", created)
	}
	if total != 15 {
		t.Errorf("total = %d, want 15", total)
	}
}

func TestEnqueuePostParseTask(t *testing.T) {
	cfg := config.DefaultConfig()
	s := &Server{
		Base: server.NewBase(cfg, nil, nil),
	}
	sender := &fakeTaskSender{}

	const eventID = "123e4567-e89b-12d3-a456-426614174000"
	if err := s.enqueuePostParseTask(sender, 42, 7, "pipeline failed", eventID); err != nil {
		t.Fatalf("enqueuePostParseTask() error = %v", err)
	}

	if len(sender.calls) != 1 {
		t.Fatalf("calls = %d, want 1", len(sender.calls))
	}
	call := sender.calls[0]
	if call.task != "tdpservice.scheduling.parser_task.post_parse" {
		t.Errorf("task = %q", call.task)
	}
	wantArgs := []interface{}{int32(42), int32(7), "pipeline failed", eventID}
	for i, want := range wantArgs {
		if call.args[i] != want {
			t.Errorf("arg %d = %#v, want %#v", i, call.args[i], want)
		}
	}
}

func TestEnqueuePostParseTaskUsesNilParseError(t *testing.T) {
	cfg := config.DefaultConfig()
	s := &Server{
		Base: server.NewBase(cfg, nil, nil),
	}
	sender := &fakeTaskSender{}

	if err := s.enqueuePostParseTask(sender, 42, 0, "", "event-id"); err != nil {
		t.Fatalf("enqueuePostParseTask() error = %v", err)
	}

	if got := sender.calls[0].args[2]; got != nil {
		t.Errorf("parse error arg = %#v, want nil", got)
	}
}

func TestEnqueuePostParseTaskSurfacesDelayError(t *testing.T) {
	cfg := config.DefaultConfig()
	s := &Server{
		Base: server.NewBase(cfg, nil, nil),
	}
	sender := &fakeTaskSender{err: fmt.Errorf("redis down")}

	err := s.enqueuePostParseTask(sender, 42, 0, "", "event-id")

	if err == nil || !strings.Contains(err.Error(), "redis down") {
		t.Fatalf("error = %v, want redis down", err)
	}
}
