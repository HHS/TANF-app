package celery

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/gocelery/gocelery"
	"github.com/gomodule/redigo/redis"
)

const resultTTLSeconds = 86400

// redisCeleryBackend stores task results in Redis and publishes them on the
// task metadata channel so Celery clients blocked on AsyncResult.get() wake up.
type redisCeleryBackend struct {
	pool *redis.Pool
}

func newRedisCeleryBackend(pool *redis.Pool) *redisCeleryBackend {
	return &redisCeleryBackend{pool: pool}
}

func (b *redisCeleryBackend) GetResult(taskID string) (*gocelery.ResultMessage, error) {
	conn := b.pool.Get()
	defer conn.Close()

	val, err := conn.Do("GET", resultKey(taskID))
	if err != nil {
		return nil, err
	}
	if val == nil {
		return nil, fmt.Errorf("result not available")
	}

	var result gocelery.ResultMessage
	if err := json.Unmarshal(val.([]byte), &result); err != nil {
		return nil, err
	}

	return &result, nil
}

func (b *redisCeleryBackend) SetResult(taskID string, result *gocelery.ResultMessage) error {
	conn := b.pool.Get()
	defer conn.Close()

	payload, err := json.Marshal(map[string]any{
		"task_id":   taskID,
		"status":    result.Status,
		"result":    result.Result,
		"traceback": result.Traceback,
		"children":  result.Children,
		"date_done": time.Now().UTC().Format(time.RFC3339),
	})
	if err != nil {
		return err
	}

	key := resultKey(taskID)
	if err := conn.Send("MULTI"); err != nil {
		return err
	}
	if err := conn.Send("SETEX", key, resultTTLSeconds, payload); err != nil {
		return err
	}
	if err := conn.Send("PUBLISH", key, payload); err != nil {
		return err
	}
	_, err = conn.Do("EXEC")
	return err
}

func resultKey(taskID string) string {
	return fmt.Sprintf("celery-task-meta-%s", taskID)
}
