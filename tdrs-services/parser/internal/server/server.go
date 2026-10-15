package server

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/db"
	"go-parser/internal/decoder"
	"go-parser/internal/logging"
	"go-parser/internal/metrics"
	"go-parser/internal/pipeline"
	"go-parser/internal/sentinel"
	"go-parser/internal/storage/reader"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// Base holds the shared dependencies for all server modes.
type Base struct {
	Config     *config.Config
	Registry   *config.Registry
	Validators *validation.ValidatorRegistry
}

// NewBase creates a Base with the given dependencies.
func NewBase(cfg *config.Config, reg *config.Registry, validators *validation.ValidatorRegistry) Base {
	return Base{
		Config:     cfg,
		Registry:   reg,
		Validators: validators,
	}
}

// ConnectDB creates a database pool and loads content types into the registry.
// The caller is responsible for closing the returned pool.
func (b *Base) ConnectDB(ctx context.Context) (*pgxpool.Pool, error) {
	if b.Config.Database.URL == "" {
		return nil, fmt.Errorf("database.url is required (set in config file, DATABASE_URL env var, or --database.url flag)")
	}

	pool, err := db.NewPool(ctx, b.Config.Database.URL, b.Config.Database)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	contentTypes, err := db.LoadContentTypes(ctx, pool)
	if err != nil {
		pool.Close()
		return nil, fmt.Errorf("failed to load content types: %w", err)
	}
	b.Registry.LoadContentTypes(contentTypes)
	logging.Info(ctx, "loaded content types from database",
		slog.String(logging.KeyStage, "database_metadata"),
		slog.Int("content_type_count", len(contentTypes)),
	)

	return pool, nil
}

// RunPipeline opens the file source, resolves the file spec, creates a decoder,
// and runs the parsing pipeline. It centralizes the shared orchestration logic
// used by all server modes.
func (b *Base) RunPipeline(ctx context.Context, source reader.FileSource, sink writer.Sink, dfCtx pipeline.DataFileContext) (result *pipeline.ParsingResult, err error) {
	return b.RunPipelineWithTablePrefix(ctx, source, sink, dfCtx, b.Registry.TablePrefix())
}

// RunPipelineWithTablePrefix runs the pipeline against the table family
// selected for an immutable parse task.
func (b *Base) RunPipelineWithTablePrefix(ctx context.Context, source reader.FileSource, sink writer.Sink, dfCtx pipeline.DataFileContext, tablePrefix string) (result *pipeline.ParsingResult, err error) {
	startTime := time.Now()
	defer func() {
		status := "success"
		if err != nil {
			status = "failed"
		}
		metrics.ObserveFileDuration(dfCtx.Program, dfCtx.Section, status, time.Since(startTime))
		metrics.RecordFileProcessed(dfCtx.Program, dfCtx.Section, status)
		recordResultMetrics(dfCtx, result)
	}()

	file, err := source.Open(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()
	defer source.Cleanup()

	registry := b.Registry.WithTablePrefix(tablePrefix)
	spec := registry.GetFileSpec(dfCtx.Program, dfCtx.Section)
	if spec == nil {
		return nil, fmt.Errorf("no file spec for %s section %d", dfCtx.Program, dfCtx.Section)
	}

	dec, err := decoder.CreateDecoder(file, spec)
	if err != nil {
		if errors.Is(err, sentinel.ErrDecoderUnknown) {
			return b.handleDecoderUnknown(ctx, sink, dfCtx, tablePrefix, startTime)
		}
		return nil, fmt.Errorf("failed to create decoder: %w", err)
	}
	defer dec.Close()

	pipelineConfig := pipeline.NewConfig(b.Config)
	pipelineConfig.TablePrefix = tablePrefix
	pipeln := pipeline.NewPipeline(sink, registry, b.Validators, pipelineConfig)
	result, err = pipeln.Process(ctx, dec, dfCtx, time.Since(startTime))
	return result, err
}

func recordResultMetrics(dfCtx pipeline.DataFileContext, result *pipeline.ParsingResult) {
	if result == nil {
		return
	}
	metrics.AddRecordsParsed(dfCtx.Program, dfCtx.Section, result.DetailRecordCount)
	if result.ErrorStats == nil {
		metrics.AddErrorsGenerated(dfCtx.Program, dfCtx.Section, "record_pre_check", result.ErrorCount)
		return
	}
	metrics.AddErrorsGenerated(dfCtx.Program, dfCtx.Section, "record_pre_check", result.ErrorStats.RecordPreCheck)
	metrics.AddErrorsGenerated(dfCtx.Program, dfCtx.Section, "field_value", result.ErrorStats.FieldValue)
	metrics.AddErrorsGenerated(dfCtx.Program, dfCtx.Section, "value_consistency", result.ErrorStats.ValueConsistency)
	metrics.AddErrorsGenerated(dfCtx.Program, dfCtx.Section, "case_consistency", result.ErrorStats.CaseConsistency)
	if remaining := result.ErrorCount - result.ErrorStats.Total(); remaining > 0 {
		metrics.AddErrorsGenerated(dfCtx.Program, dfCtx.Section, "record_pre_check", remaining)
	}
}

func (b *Base) handleDecoderUnknown(ctx context.Context, sink writer.Sink, dfCtx pipeline.DataFileContext, tablePrefix string, startTime time.Time) (*pipeline.ParsingResult, error) {
	parserErr := writer.SerializeParserError(
		1,
		sentinel.DecoderUnknownMessage,
		validation.ErrorTypePreCheck,
		dfCtx.DatafileID,
	)
	errorTable := config.ParserErrorTableName(tablePrefix)
	if _, err := sink.Flush(ctx, errorTable, writer.ParserErrorColumns(), [][]any{parserErr}); err != nil {
		return nil, fmt.Errorf("write decoder unknown parser error: %w", err)
	}
	return &pipeline.ParsingResult{
		RecordCounts: map[string]int64{"parser_error": 1},
		ErrorCount:   1,
		ErrorStats:   &pipeline.ErrorStats{RecordPreCheck: 1},
		Duration:     time.Since(startTime),
	}, nil
}
