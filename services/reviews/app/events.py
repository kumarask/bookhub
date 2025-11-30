"""
Pub/Sub event utilities for Reviews Service.

Provides functions to publish events to Redis channels for inter-service communication.
"""

import redis.asyncio as redis
import json
from app.config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


async def publish_event(event_name: str, payload: dict):
    """
    Publish an event to a Redis channel.

    Args:
        event_name (str): Name of the event (used to construct the Redis channel).
        payload (dict): Dictionary payload containing event data.

    Example:
        await publish_event("review.created", {"review_id": "1234-5678"})
    """
    channel = f"events:{event_name}"
    await redis_client.publish(channel, json.dumps(payload))
