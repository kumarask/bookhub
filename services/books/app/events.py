import redis.asyncio as redis
import json

REDIS_URL = "redis://localhost:6379"
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

async def publish_event(event_name: str, payload: dict):
    channel = f"events:{event_name}"
    await redis_client.publish(channel, json.dumps(payload))
