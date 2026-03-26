package main

import (
	"context"
	"log"
	"os"
	"runtime/pprof"

	"go-parser/internal/config"
	"go-parser/internal/server/celery"
	"go-parser/internal/server/local"
	"go-parser/internal/validation"
)

func main() {
	// Parse CLI flags (Kong)
	cli, ctx, err := config.ParseCLI(os.Args[1:])
	if err != nil {
		log.Fatalf("Failed to parse CLI: %v", err)
	}

	// Load config file with env var interpolation
	cfg, err := config.LoadConfig(cli.ConfigFile)
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Apply CLI flag overrides (highest precedence)
	cli.ApplyTo(cfg, ctx)

	// CPU profiling
	if cli.CPUProfile != "" {
		f, err := os.Create(cli.CPUProfile)
		if err != nil {
			log.Fatal(err)
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
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Load and compile validators
	validators, err := validation.NewRegistry(cfg, reg)
	if err != nil {
		log.Fatalf("Failed to load validators: %v", err)
	}

	// ---- Server mode dispatch ----
	switch cfg.Server.Mode {
	case "local":
		if err := local.New(cfg, reg, validators).Run(bgCtx); err != nil {
			log.Fatalf("Local mode failed: %v", err)
		}
	case "celery":
		mode, err := celery.New(cfg, reg, validators)
		if err != nil {
			log.Fatalf("Failed to initialize celery mode: %v", err)
		}
		if err := mode.Run(bgCtx); err != nil {
			log.Fatalf("Celery mode failed: %v", err)
		}
	case "grpc":
		log.Fatal("gRPC server mode not yet implemented")
	case "http":
		log.Fatal("HTTP server mode not yet implemented")
	default:
		log.Fatalf("unknown server mode: %s", cfg.Server.Mode)
	}

	// Memory profiling (after work completes)
	if cli.MemProfile != "" {
		f, err := os.Create(cli.MemProfile)
		if err != nil {
			log.Fatal(err)
		}
		pprof.WriteHeapProfile(f)
		f.Close()
	}
}
