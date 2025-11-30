"""
Event publishing utilities using Redis Pub/Sub.

This module provides a helper function to publish application events
to Redis channels. It is useful for implementing event-driven features,
real-time notifications, background workers, or microservice communication.

Components:
    - redis_client: Asynchronous Redis client configured from the application settings.
    - publish_event: Publishes a JSON-encoded payload to a Redis event channel.
"""

import redis.asyncio as redis
import json
from app.config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


async def publish_event(event_name: str, payload: dict):
    """
    Publish an event payload to a Redis Pub/Sub channel.

    Args:
        event_name (str): Name of the event channel (without prefix).
        payload (dict): Data to send to subscribers. It will be JSON-encoded.

    Returns:
        None

    Notes:
        - The event is published to a channel named `events:{event_name}`.
        - Subscribers listening on the channel will receive the encoded payload.
    """
    channel = f"events:{event_name}"
    await redis_client.publish(channel, json.dumps(payload))
