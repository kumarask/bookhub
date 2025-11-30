"""
app.cache

Redis Cache Utility Module.

Provides asynchronous helper functions for interacting with Redis, including
getting, setting, and deleting cached values.

Functions
---------
- get_cache(key: str) -> str | None
    Retrieve a cached value by key.
- set_cache(key: str, value: str, ttl: int) -> None
    Set a value in the cache with a time-to-live (TTL) in seconds.
- delete_cache(key: str) -> None
    Delete a value from the cache by key.

Author: Your Name <your.email@example.com>
"""

import redis.asyncio as redis
from app.config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


async def get_cache(key: str):
    """
    Retrieve a cached value from Redis.

    Args:
        key (str): The cache key to retrieve.

    Returns:
        str | None: The cached value if it exists, else None.
    """
    return await redis_client.get(key)


async def set_cache(key: str, value: str, ttl: int):
    """
    Set a value in Redis cache with an expiration time.

    Args:
        key (str): The cache key to set.
        value (str): The value to store.
        ttl (int): Time-to-live in seconds for the cached value.
    """
    await redis_client.set(key, value, ex=ttl)


async def delete_cache(key: str):
    """
    Delete a value from Redis cache.

    Args:
        key (str): The cache key to delete.
    """
    await redis_client.delete(key)
