"""Failure policies and network bounds for Redis caches."""

import json
import runpy
import socket
from pathlib import Path
from threading import Event, Thread
from time import monotonic
from unittest.mock import patch

from django.core.cache.backends.redis import RedisCache

import pytest
from redis.exceptions import ConnectionError, ResponseError, TimeoutError

from tdpservice.cache import OptionalRedisCache
from tdpservice.settings.common import Common, init_sentry


@pytest.mark.parametrize("error", [ConnectionError, TimeoutError])
def test_optional_cache_returns_caller_default_on_read_failure(error) -> None:
    """Redis transport failures behave like a miss, including custom defaults."""
    cache = OptionalRedisCache("redis://localhost/1", {})
    default = object()
    with patch.object(RedisCache, "get", side_effect=error):
        assert cache.get("missing", default=default) is default


@pytest.mark.parametrize("operation", ["get", "set", "clear"])
def test_optional_cache_does_not_hide_other_errors(operation: str) -> None:
    """Server and programming errors must remain visible."""
    cache = OptionalRedisCache("redis://localhost/1", {})
    args = {"get": ("key",), "set": ("key", "value"), "clear": ()}
    with patch.object(RedisCache, operation, side_effect=ResponseError):
        with pytest.raises(ResponseError):
            getattr(cache, operation)(*args[operation])


@pytest.mark.parametrize("error", [ConnectionError, TimeoutError])
def test_optional_cache_write_and_clear_failures_are_logged(error, caplog) -> None:
    """Failed cache updates are observable without failing the caller."""
    cache = OptionalRedisCache("redis://localhost/1", {"KEY_PREFIX": "optional"})
    with patch.object(RedisCache, "set", side_effect=error):
        assert cache.set("key", "value") is None
    with patch.object(RedisCache, "clear", side_effect=error):
        assert cache.clear() is False
    assert "optional write failed" in caplog.text
    assert "optional invalidation failed" in caplog.text


@pytest.mark.parametrize("environment", ["prod", "staging", "develop"])
def test_cloudgov_preserves_cache_failure_policies(environment, monkeypatch) -> None:
    """Deployed settings retain the same bounds and optional/strict backends."""
    space = "prod" if environment == "prod" else "staging"
    credentials = {
        "db_name": "test",
        "username": "test",
        "password": "test",
        "host": "localhost",
        "port": 6379,
        "bucket": "test",
        "access_key_id": "test",
        "secret_access_key": "test",
        "endpoint": "localhost",
        "region": "test",
    }
    services = {
        "aws-rds": [{"instance_name": f"tdp-db-{space}", "credentials": credentials}],
        "s3": [
            {"instance_name": f"tdp-{name}-{space}", "credentials": credentials}
            for name in ("datafiles", "staticfiles")
        ],
        "aws-elasticache-redis": [{"credentials": credentials}],
    }
    monkeypatch.setenv("VCAP_SERVICES", json.dumps(services))
    monkeypatch.setenv(
        "VCAP_APPLICATION",
        json.dumps(
            {
                "name": f"tdp-backend-{environment}",
                "space_name": f"tanf-{space}",
            }
        ),
    )
    cloudgov_path = Path(__file__).resolve().parents[1] / "settings" / "cloudgov.py"
    deployed_caches = runpy.run_path(str(cloudgov_path))["CloudGov"].CACHES
    for alias in ("stts", "feature-flags", "throttle"):
        assert deployed_caches[alias]["OPTIONS"] == Common.CACHES[alias]["OPTIONS"]
        expected = (
            "django.core.cache.backends.redis.RedisCache"
            if alias == "throttle"
            else "tdpservice.cache.OptionalRedisCache"
        )
        assert deployed_caches[alias]["BACKEND"] == expected
        assert deployed_caches[alias]["KEY_PREFIX"] == f"{environment}-{alias}"


@pytest.mark.parametrize("alias", ["stts", "feature-flags", "throttle"])
def test_cache_connection_has_bounded_waits_and_no_retries(alias: str) -> None:
    """Inspect actual connection options without opening a network connection."""
    config = Common.CACHES[alias]
    cache = RedisCache(config["LOCATION"], config)
    pool = cache._cache.get_client().connection_pool
    connection = pool.make_connection()

    assert connection.socket_connect_timeout == 1
    assert connection.socket_timeout == 1
    assert connection.retry.get_retries() == 0


def test_unresponsive_redis_read_is_bounded() -> None:
    """A server accepting GET without replying cannot hold the caller indefinitely."""
    received_get = Event()
    release_server = Event()
    errors = []

    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        server.settimeout(5)

        def serve() -> None:
            try:
                with server.accept()[0] as client:
                    client.settimeout(5)
                    with client.makefile("rb") as stream:
                        while True:
                            header = stream.readline()
                            if not header:
                                return
                            count = int(header[1:])
                            command = []
                            for _ in range(count):
                                length = int(stream.readline()[1:])
                                command.append(stream.read(length))
                                stream.read(2)
                            if command[0].upper() == b"GET":
                                received_get.set()
                                release_server.wait(5)
                                return
                            client.sendall(b"+OK\r\n")
            except Exception as exc:
                errors.append(exc)

        worker = Thread(target=serve, daemon=True)
        worker.start()
        config = Common.CACHES["stts"]
        cache = OptionalRedisCache(
            f"redis://127.0.0.1:{server.getsockname()[1]}/1", config
        )
        try:
            start = monotonic()
            assert cache.get("test") is None
            elapsed = monotonic() - start
            assert received_get.is_set()
            assert elapsed < 3
        finally:
            release_server.set()
            cache.close()
            worker.join(timeout=6)
        assert not worker.is_alive()
        assert not errors


def test_sentry_uses_deployed_release(monkeypatch) -> None:
    """Sentry receives the revision supplied by deployment."""
    monkeypatch.setenv("SENTRY_RELEASE", "test-deployed-revision")
    with patch("tdpservice.settings.common.sentry_sdk.init") as initialize:
        init_sentry("", environment="test")
    assert initialize.call_args.kwargs["release"] == "test-deployed-revision"
