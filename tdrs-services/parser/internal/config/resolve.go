package config

import (
	"fmt"
	"path/filepath"
	"sort"

	"github.com/bmatcuk/doublestar/v4"
)

// ResolveFileGlobs expands a list of glob patterns relative to baseDir
// into deduplicated, sorted absolute file paths. Supports ** for recursive
// directory matching via the doublestar library.
func ResolveFileGlobs(baseDir string, patterns []string) ([]string, error) {
	seen := make(map[string]struct{})
	var files []string

	for _, pattern := range patterns {
		abs := filepath.Join(baseDir, pattern)
		matches, err := doublestar.FilepathGlob(abs)
		if err != nil {
			return nil, fmt.Errorf("expanding glob %q: %w", pattern, err)
		}

		for _, m := range matches {
			if _, ok := seen[m]; !ok {
				seen[m] = struct{}{}
				files = append(files, m)
			}
		}
	}

	sort.Strings(files)
	return files, nil
}
