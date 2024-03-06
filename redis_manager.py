import redis
import aioredis

try:
    redis_client = redis.StrictRedis(host='localhost', port=6390, db=0)

except Exception as e:
    print(f"Error connecting to Redis: {e}")


def get_redis_client():
    client = aioredis.Redis(host='localhost', port=6390, db=0)
    return client
