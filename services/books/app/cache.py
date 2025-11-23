import redis.asyncio as redis
import json

REDIS_URL = "redis://localhost:6379"
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

async def get_cached_book(book_id: str):
    data = await redis_client.get(f"book:{book_id}")
    if data:
        return json.loads(data)
    return None

async def set_cached_book(book_id: str, book_data: dict, ttl=3600):
    await redis_client.set(f"book:{book_id}", json.dumps(book_data), ex=ttl)

async def delete_cached_book(book_id: str):
    await redis_client.delete(f"book:{book_id}")
