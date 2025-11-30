"""
Redis Pub/Sub utility module.

This module provides a Redis client for publishing events using
Redis Pub/Sub. Events are published to channels prefixed with 'events:'.
"""

import redis.asyncio as redis
import json
from app.config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


async def publish_event(event_name: str, payload: dict):
    """
    Publish an event to a Redis channel.

    Args:
        event_name (str): Name of the event (used to build the channel name)
        payload (dict): Data to send with the event, will be JSON-encoded

    Example:
        await publish_event("order.created", {"order_id": "1234"})
    """
    channel = f"events:{event_name}"
    await redis_client.publish(channel, json.dumps(payload))
