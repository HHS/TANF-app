"""Redis cache behavior for optional database-backed lookups."""

import logging
from typing import Any

from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.redis import RedisCache

from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


class OptionalRedisCache(RedisCache):
    """Treat Redis transport failures as misses or unsuccessful writes."""

    def get(self, key: str, default: Any = None, version: int | None = None) -> Any:
        """Return the caller's default when Redis cannot serve a lookup."""
        try:
            return super().get(key, default=default, version=version)
        except (ConnectionError, TimeoutError):
            logger.warning("Optional cache %s read failed", self.key_prefix)
            return default

    def set(
        self,
        key: str,
        value: Any,
        timeout: Any = DEFAULT_TIMEOUT,
        version: int | None = None,
    ) -> None:
        """Allow database-backed responses to succeed when a cache write fails."""
        try:
            super().set(key, value, timeout=timeout, version=version)
        except (ConnectionError, TimeoutError):
            logger.warning("Optional cache %s write failed", self.key_prefix)

    def clear(self) -> bool:
        """Keep database changes available when cache invalidation fails."""
        try:
            return super().clear()
        except (ConnectionError, TimeoutError):
            logger.warning(
                "Optional cache %s invalidation failed; stale entries may remain until expiry",
                self.key_prefix,
            )
            return False
