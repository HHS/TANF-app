package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestResolveFileGlobs_DoubleStarPattern(t *testing.T) {
	dir := t.TempDir()

	// Create nested directory structure
	dirs := []string{
		filepath.Join(dir, "schemas", "tanf"),
		filepath.Join(dir, "schemas", "common"),
	}
	for _, d := range dirs {
		os.MkdirAll(d, 0755)
	}

	files := []string{
		filepath.Join(dir, "schemas", "tanf", "t1.yaml"),
		filepath.Join(dir, "schemas", "tanf", "t2.yaml"),
		filepath.Join(dir, "schemas", "common", "header.yaml"),
	}
	for _, f := range files {
		os.WriteFile(f, []byte("test"), 0644)
	}

	result, err := ResolveFileGlobs(dir, []string{"schemas/**/*.yaml"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(result) != 3 {
		t.Errorf("got %d files, want 3: %v", len(result), result)
	}
}

func TestResolveFileGlobs_SingleGlob(t *testing.T) {
	dir := t.TempDir()

	// Create flat files and a nested one
	os.MkdirAll(filepath.Join(dir, "sub"), 0755)
	os.WriteFile(filepath.Join(dir, "a.yaml"), []byte("test"), 0644)
	os.WriteFile(filepath.Join(dir, "b.yaml"), []byte("test"), 0644)
	os.WriteFile(filepath.Join(dir, "sub", "c.yaml"), []byte("test"), 0644)

	// Single * should NOT match nested files
	result, err := ResolveFileGlobs(dir, []string{"*.yaml"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(result) != 2 {
		t.Errorf("got %d files, want 2 (flat only): %v", len(result), result)
	}
}

func TestResolveFileGlobs_NoMatches(t *testing.T) {
	dir := t.TempDir()

	result, err := ResolveFileGlobs(dir, []string{"nonexistent/**/*.yaml"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(result) != 0 {
		t.Errorf("got %d files, want 0: %v", len(result), result)
	}
}

func TestResolveFileGlobs_MultiplePatterns(t *testing.T) {
	dir := t.TempDir()

	os.MkdirAll(filepath.Join(dir, "schemas", "tanf"), 0755)
	os.MkdirAll(filepath.Join(dir, "filespecs"), 0755)
	os.WriteFile(filepath.Join(dir, "schemas", "tanf", "t1.yaml"), []byte("test"), 0644)
	os.WriteFile(filepath.Join(dir, "filespecs", "s1.yaml"), []byte("test"), 0644)

	result, err := ResolveFileGlobs(dir, []string{
		"schemas/**/*.yaml",
		"filespecs/*.yaml",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(result) != 2 {
		t.Errorf("got %d files, want 2: %v", len(result), result)
	}
}

func TestResolveFileGlobs_Deduplication(t *testing.T) {
	dir := t.TempDir()

	os.MkdirAll(filepath.Join(dir, "schemas"), 0755)
	os.WriteFile(filepath.Join(dir, "schemas", "t1.yaml"), []byte("test"), 0644)

	// Two patterns that match the same file
	result, err := ResolveFileGlobs(dir, []string{
		"schemas/*.yaml",
		"schemas/t1.yaml",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(result) != 1 {
		t.Errorf("got %d files, want 1 (deduplicated): %v", len(result), result)
	}
}
