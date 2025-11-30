"""
Redis-based rate limiting utility for API Gateway.

This module provides a mechanism to enforce request rate limits
based on the type of user making the request. Rate limits are
stored in Redis with a TTL of 60 seconds.

Rate limiting rules:
- Unauthenticated requests: 20 requests per minute per IP
- Authenticated requests: 100 requests per minute per user
- Admin requests: 500 requests per minute per user
"""

import redis.asyncio as redis
from fastapi import HTTPException, Request
from app.config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


async def rate_limit(request: Request, user=None):
    """
    Enforce rate limiting for incoming requests.

    Args:
        request (Request): The FastAPI request object.
        user (dict, optional): Authenticated user information, containing 'id' and optionally 'is_admin'.

    Raises:
        HTTPException: If the request exceeds the allowed rate limit (HTTP 429).

    Behavior:
        - Tracks request counts in Redis per IP for unauthenticated users.
        - Tracks request counts in Redis per user ID for authenticated users.
        - Resets count every 60 seconds (per minute).
    """
    ip = request.client.host
    key = f"rl:{ip}"
    limit = 20  # default unauthenticated

    if user:
        if user.get("is_admin"):
            limit = 500
        else:
            limit = 100
        key = f"rl:user:{user['id']}"

    current = await redis_client.get(key)
    if current and int(current) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    pipe = redis_client.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, 60)
    await pipe.execute()
