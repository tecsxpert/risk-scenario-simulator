import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=2
    )
    client.ping()
    redis_available = True
except Exception as e:
    print("Redis connection failed:", e)
    client = None
    redis_available = False


def get_cache(key):
    if redis_available:
        return client.get(key)
    return None


def set_cache(key, value):
    if redis_available:
        client.setex(key, 3600, value)