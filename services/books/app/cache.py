"""
Utility functions for caching and retrieving book data using Redis.

This module provides asynchronous helper functions for interacting with a
Redis cache. It enables efficient storage, retrieval, and deletion of
book-related data to improve application performance and reduce database load.

Functions:
    - get_cached_book: Retrieve a cached book by its ID.
    - set_cached_book: Store book data in the cache with an optional TTL.
    - delete_cached_book: Remove a cached book entry from Redis.
"""

import json
from app.deps import get_redis


async def get_cached_book(book_id: str):
    """
    Retrieve book data from Redis cache.

    Args:
        book_id (str): Unique identifier of the book to fetch from cache.

    Returns:
        dict | None: The cached book data if present, otherwise None.
    """
    data = await get_redis().get(f"book:{book_id}")
    if data:
        return data
    return None


async def set_cached_book(book_id: str, book_data: dict, ttl=3600):
    """
    Store book data in Redis with an optional time-to-live (TTL).

    Args:
        book_id (str): Unique identifier of the book to cache.
        book_data (dict): The book data to store in Redis.
        ttl (int, optional): Time in seconds before the cache expires.
                             Defaults to 3600 (1 hour).

    Returns:
        None
    """
    await get_redis().set(f"book:{book_id}", book_data, ex=ttl)


async def delete_cached_book(book_id: str):
    """
    Remove a cached book entry from Redis.

    Args:
        book_id (str): Unique identifier of the book to remove from cache.

    Returns:
        None
    """
    await get_redis().delete(f"book:{book_id}")
