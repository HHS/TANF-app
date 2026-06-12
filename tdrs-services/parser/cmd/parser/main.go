package main

import (
	"context"
	"log/slog"
	"os"
	"runtime/pprof"

	"go-parser/internal/config"
	"go-parser/internal/logging"
	"go-parser/internal/server/celery"
	"go-parser/internal/server/local"
	"go-parser/internal/validation"
)

func main() {
	if err := logging.Configure("info"); err != nil {
		fatal("Failed to configure logging", err)
	}

	// Parse CLI flags (Kong)
	cli, ctx, err := config.ParseCLI(os.Args[1:])
	if err != nil {
		fatal("Failed to parse CLI", err)
	}

	// Load config file with env var interpolation
	cfg, err := config.LoadConfig(cli.ConfigFile)
	if err != nil {
		fatal("Failed to load config", err)
	}

	// Apply CLI flag overrides (highest precedence)
	cli.ApplyTo(cfg, ctx)
	if err := logging.Configure(cfg.Global.LogLevel); err != nil {
		fatal("Failed to configure logging", err)
	}

	// CPU profiling
	if cli.CPUProfile != "" {
		f, err := os.Create(cli.CPUProfile)
		if err != nil {
			fatal("Failed to create CPU profile", err)
		}
		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
	}

	bgCtx := context.Background()

	// Load schemas and filespecs via glob patterns from config
	// TODO: Need to revisit storing the object pools on the schemas. Since the registry will exist for as long as the
	// celery worker does, the object pools could grow to an enormous size since there isn't a way to clear them after a
	// parsing run. We should consider implementing/importing a better solution that allows clearing. Or, we could reload
	// the registry each time a new parsing request comes in (simpler).
	reg, err := config.NewRegistry(cfg)
	if err != nil {
		fatal("Failed to load configuration", err)
	}

	// Load and compile validators
	validators, err := validation.NewRegistry(cfg, reg)
	if err != nil {
		fatal("Failed to load validators", err)
	}

	// ---- Server mode dispatch ----
	switch cfg.Server.Mode {
	case "local":
		if err := local.New(cfg, reg, validators).Run(bgCtx); err != nil {
			fatal("Local mode failed", err)
		}
	case "celery":
		mode, err := celery.New(cfg, reg, validators)
		if err != nil {
			fatal("Failed to initialize celery mode", err)
		}
		if err := mode.Run(bgCtx); err != nil {
			fatal("Celery mode failed", err)
		}
	case "grpc":
		fatal("gRPC server mode not yet implemented", nil)
	case "http":
		fatal("HTTP server mode not yet implemented", nil)
	default:
		logging.Fatal("unknown server mode", slog.String("mode", cfg.Server.Mode))
	}

	// Memory profiling (after work completes)
	if cli.MemProfile != "" {
		f, err := os.Create(cli.MemProfile)
		if err != nil {
			fatal("Failed to create memory profile", err)
		}
		pprof.WriteHeapProfile(f)
		f.Close()
	}
}

func fatal(message string, err error) {
	if err != nil {
		logging.Fatal(message, slog.String(logging.KeyError, err.Error()))
	}
	logging.Fatal(message)
}
