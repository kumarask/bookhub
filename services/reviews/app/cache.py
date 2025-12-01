"""
Redis caching utilities for the Reviews Service.

Provides async helper functions to get, set, and delete cached data in Redis.
Used for caching book reviews, review summaries, and user-specific review pages.

Caching Strategy:
- Cache book reviews: `reviews:book:{book_id}:page:{page}` (TTL: 10 minutes)
- Cache review summary: `reviews:summary:{book_id}` (TTL: 15 minutes)
- Cache user reviews: `reviews:user:{user_id}:page:{page}` (TTL: 10 minutes)
"""
from app.deps import get_redis


async def get_cache(key: str):
    """
    Retrieve a value from Redis cache by its key.

    Args:
        key (str): The cache key to look up.

    Returns:
        str | None: Cached value if exists, otherwise None.
    """
    return await get_redis().get(key)


async def set_cache(key: str, value: str, ttl: int):
    """
    Store a value in Redis cache with a TTL (time-to-live).

    Args:
        key (str): The cache key.
        value (str): The value to store.
        ttl (int): Time-to-live in seconds before the cache expires.

    Returns:
        None
    """
    await get_redis().set(key, value, ex=ttl)


async def delete_cache(key: str):
    """
    Delete a key from Redis cache.

    Args:
        key (str): The cache key to delete.

    Returns:
        None
    """
    await get_redis().delete(key)
