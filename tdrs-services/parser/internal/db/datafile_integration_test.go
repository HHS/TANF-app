package db

import (
	"context"
	"encoding/json"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

func stateTransitionTestPool(t *testing.T) (*pgxpool.Pool, context.Context) {
	t.Helper()
	databaseURL := os.Getenv("TEST_DATABASE_URL")
	if databaseURL == "" {
		t.Skip("set TEST_DATABASE_URL to run PostgreSQL state transition tests")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	t.Cleanup(cancel)
	conn, err := pgx.Connect(ctx, databaseURL)
	if err != nil {
		t.Fatal(err)
	}
	schema := "state_transition_test_" + strings.ReplaceAll(newLogEventUUID().String(), "-", "")
	schemaName := pgx.Identifier{schema}.Sanitize()
	if _, err := conn.Exec(ctx, "CREATE SCHEMA "+schemaName); err != nil {
		_ = conn.Close(ctx)
		t.Fatal(err)
	}
	t.Cleanup(func() {
		cleanupCtx, cleanupCancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cleanupCancel()
		if _, err := conn.Exec(cleanupCtx, "DROP SCHEMA "+schemaName+" CASCADE"); err != nil {
			t.Error(err)
		}
		_ = conn.Close(cleanupCtx)
	})
	poolConfig, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		t.Fatal(err)
	}
	poolConfig.ConnConfig.RuntimeParams["search_path"] = schema
	pool, err := pgxpool.NewWithConfig(ctx, poolConfig)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(pool.Close)
	_, err = pool.Exec(ctx, `
		CREATE TABLE data_files_datafile (id integer PRIMARY KEY, state text NOT NULL);
		CREATE TABLE shadow_data_files_datafile (LIKE data_files_datafile INCLUDING ALL);
		INSERT INTO data_files_datafile VALUES (42, 'parse_started');
		INSERT INTO shadow_data_files_datafile VALUES (42, 'parse_started');
		CREATE TABLE django_content_type (
			id integer PRIMARY KEY, app_label text NOT NULL, model text NOT NULL,
			UNIQUE (app_label, model)
		);
		INSERT INTO django_content_type VALUES
			(1, 'data_files', 'datafile'), (2, 'data_files', 'shadowdatafile');
		CREATE TABLE core_baselog (
			id bigserial PRIMARY KEY, object_id text NOT NULL, event_id uuid NOT NULL,
			event_type text NOT NULL, note text NOT NULL, metadata jsonb NOT NULL,
			source text, task_name text, celery_task_id text, created_at timestamptz NOT NULL,
			actor_id uuid, content_type_id integer NOT NULL REFERENCES django_content_type
		);
		CREATE TABLE data_files_datafilestatetransition (
			baselog_ptr_id bigint PRIMARY KEY REFERENCES core_baselog,
			previous_state text NOT NULL, next_state text NOT NULL, reparse_meta_id integer
		);
	`)
	if err != nil {
		t.Fatal(err)
	}
	return pool, ctx
}

func TestUpdateDataFileStatePersistsSeparateCorrelatedHistories(t *testing.T) {
	pool, ctx := stateTransitionTestPool(t)
	transitionContext := DataFileStateTransitionContext{
		EventID:       newLogEventUUID().String(),
		Note:          "Go parser parsing completed",
		Source:        "go_parser",
		TaskName:      "tdpservice.scheduling.parser_task.go_parse",
		CeleryTaskID:  newLogEventUUID().String(),
		ReparseMetaID: 7,
		Metadata:      map[string]any{"stage": "complete"},
	}
	for _, target := range []struct {
		table string
		model string
	}{
		{shadowDataFileTable, "shadowdatafile"},
		{productionDataFileTable, "datafile"},
	} {
		for range 2 {
			if err := UpdateDataFileState(ctx, pool, target.table, 42, "parse_completed", transitionContext); err != nil {
				t.Fatal(err)
			}
		}
		var previousState, nextState, eventID, taskID, source, taskName, note, objectID string
		var reparseID int32
		var metadataJSON []byte
		err := pool.QueryRow(ctx, `
				SELECT previous_state, next_state, event_id::text, celery_task_id,
				       source, task_name, note, object_id, reparse_meta_id, metadata
				FROM data_files_datafilestatetransition AS transition
				JOIN core_baselog AS log ON log.id = transition.baselog_ptr_id
				JOIN django_content_type AS ct ON ct.id = log.content_type_id
				WHERE ct.app_label = 'data_files' AND ct.model = $1
			`, target.model).Scan(&previousState, &nextState, &eventID, &taskID,
			&source, &taskName, &note, &objectID, &reparseID, &metadataJSON)
		if err != nil {
			t.Fatal(err)
		}
		if previousState != "parse_started" || nextState != "parse_completed" || objectID != "42" {
			t.Fatalf("unexpected transition: %s -> %s for %s", previousState, nextState, objectID)
		}
		if eventID != transitionContext.EventID || taskID != transitionContext.CeleryTaskID ||
			source != transitionContext.Source || taskName != transitionContext.TaskName ||
			note != transitionContext.Note || reparseID != transitionContext.ReparseMetaID {
			t.Fatal("transition did not preserve run context")
		}
		var metadata map[string]any
		if err := json.Unmarshal(metadataJSON, &metadata); err != nil {
			t.Fatal(err)
		}
		if metadata["stage"] != "complete" || metadata["event_id"] != eventID {
			t.Fatalf("unexpected metadata: %v", metadata)
		}
		var productionState, shadowState string
		if err := pool.QueryRow(ctx, `
				SELECT production.state, shadow.state
				FROM data_files_datafile production JOIN shadow_data_files_datafile shadow USING (id)
				WHERE id = 42
			`).Scan(&productionState, &shadowState); err != nil {
			t.Fatal(err)
		}
		if shadowState != "parse_completed" ||
			(target.model == "shadowdatafile" && productionState != "parse_started") ||
			(target.model == "datafile" && productionState != "parse_completed") {
			t.Fatalf("unexpected states: production=%s, shadow=%s", productionState, shadowState)
		}
	}
	var count int
	if err := pool.QueryRow(ctx, "SELECT count(*) FROM core_baselog").Scan(&count); err != nil {
		t.Fatal(err)
	}
	if count != 2 {
		t.Fatalf("got %d logs, want one per file with no duplicates for unchanged states", count)
	}
}

func TestUpdateDataFileStateRollsBackWhenAuditInsertFails(t *testing.T) {
	for _, table := range []string{productionDataFileTable, shadowDataFileTable} {
		t.Run(table, func(t *testing.T) {
			pool, ctx := stateTransitionTestPool(t)
			if _, err := pool.Exec(ctx, `
				ALTER TABLE data_files_datafilestatetransition
				ADD CONSTRAINT reject_failed_transition CHECK (next_state <> 'parse_failed')
			`); err != nil {
				t.Fatal(err)
			}
			if err := UpdateDataFileState(ctx, pool, table, 42, "parse_failed"); err == nil {
				t.Fatal("expected audit insert failure")
			}
			var state string
			if err := pool.QueryRow(ctx, "SELECT state FROM "+pgx.Identifier{table}.Sanitize()+" WHERE id = 42").Scan(&state); err != nil {
				t.Fatal(err)
			}
			var count int
			if err := pool.QueryRow(ctx, "SELECT count(*) FROM core_baselog").Scan(&count); err != nil {
				t.Fatal(err)
			}
			if state != "parse_started" || count != 0 {
				t.Fatalf("rollback left state=%s and %d logs", state, count)
			}
		})
	}
}
