package db

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
)

// LoadContentTypes queries django_content_type to get content type IDs for search_indexes models.
// Returns a map from model name (e.g., "tanf_t1") to content type ID.
func LoadContentTypes(ctx context.Context, pool *pgxpool.Pool) (map[string]int32, error) {
	query := `
		SELECT model, id
		FROM django_content_type
		WHERE app_label = 'search_indexes'
	`

	rows, err := pool.Query(ctx, query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	result := make(map[string]int32)
	for rows.Next() {
		var model string
		var id int32
		if err := rows.Scan(&model, &id); err != nil {
			return nil, err
		}
		result[model] = id
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return result, nil
}
