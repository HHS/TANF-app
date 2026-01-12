package worker

import (
	"log"
	"log/slog"

	"github.com/gocelery/gocelery"
	"github.com/gomodule/redigo/redis"
)

type CeleryWorker interface {
	Start() error
	initClient() (*gocelery.CeleryClient, error)
	initTasks()
}

type RedisWorker struct {
	pool   *redis.Pool
	Client *gocelery.CeleryClient
	tasks  map[string]interface{}
}

func (w *RedisWorker) initTasks() {
	for taskName, task := range w.tasks {
		w.Client.Register(taskName, task)
	}
}

func (w *RedisWorker) initClient(redisPool *redis.Pool) (*gocelery.CeleryClient, error) {
	client, err := gocelery.NewCeleryClient(
		gocelery.NewRedisBroker(redisPool),
		&gocelery.RedisCeleryBackend{
			Pool: redisPool,
		},
		1,
	)

	return client, err
}

func NewRedisWorker(redisUrl string, tasks map[string]interface{}) (*RedisWorker, error) {
	redisPool := &redis.Pool{
		Dial: func() (redis.Conn, error) {
			c, err := redis.DialURL(redisUrl)
			if err != nil {
				log.Fatal("Failed to connect to redis: " + err.Error())
				return nil, err
			}
			return c, nil
		},
	}

	w := &RedisWorker{
		pool:  redisPool,
		tasks: tasks,
	}

	client, err := w.initClient(redisPool)
	if err != nil {
		return nil, err
	}
	w.Client = client

	w.initTasks()

	return w, nil
}

func (w *RedisWorker) Start() error {
	w.Client.StartWorker()
	slog.Info("Starting Worker")
	w.Client.WaitForStopWorker()
	slog.Info("Worker stopped")

	// Need to figure out proper error handling if the worker dies
	return nil
}
