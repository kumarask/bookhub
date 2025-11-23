"""Simple Redis-backed rate limiter used by the API gateway.

This module provides a small, synchronous Redis-backed rate limiter
class intended for lightweight, per-identity request throttling in the
gateway. The limiter stores a counter in Redis per identity (for
example a client IP or an authorization token) and uses an expiry to
implement a sliding time window.

Configuration
- Instantiate :class:`RateLimiter` with a Redis URL (default
    ``redis://redis:6379/0``). The class exposes a ``limits`` mapping that
    can be adjusted at runtime to change allowed requests per window for
    different identity classes (``unauth``, ``auth``, ``admin`` in the
    scaffold).

Behavior
- ``allow_request(identity)`` increments a Redis key for the identity
    and returns ``True`` when the request is within the configured limit
    or ``False`` when the limit is exceeded. On Redis errors the limiter
    falls back to allowing requests to avoid accidentally blocking traffic.

Notes
- This implementation is intentionally simple and does not provide
    strict atomic windowing guarantees beyond Redis INCR+EXPIRE. For
    production use consider using a Lua script for atomic increments with
    expiry, token bucket algorithms, or a dedicated rate-limiting service.
"""

import redis


class RateLimiter:
    def __init__(self, redis_url="redis://redis:6379/0"):
        """Create a RateLimiter instance.

        Args:
            redis_url (str): connection URL for Redis.
        """
        self.r = redis.from_url(redis_url)
        # limits mapping: role -> (max_requests, window_seconds)
        self.limits = {"unauth": (20, 60), "auth": (100, 60), "admin": (500, 60)}

    async def allow_request(self, identity):
        """Check whether a request from ``identity`` is allowed.

        The method increments the Redis counter for the identity and sets
        the expiry on the first increment. If the counter exceeds the
        configured limit this returns ``False``. Any Redis error causes a
        permissive fallback (``True``) so that rate limiter failures don't
        block traffic.

        Args:
            identity (str): a string identifying the requester (IP, token,
                or another stable identifier).

        Returns:
            bool: ``True`` when the request is allowed, ``False`` when the
            rate limit has been exceeded.
        """
        key = f"rate:{identity}"
        # default to the "auth" bucket; production code should classify
        # identity into a role (unauth/auth/admin) before calling this
        limit, window = self.limits["auth"]
        try:
            cur = self.r.incr(key)
            if cur == 1:
                self.r.expire(key, window)
            if cur > limit:
                return False
            return True
        except Exception:
            # permissive fallback on Redis errors
            return True
