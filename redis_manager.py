import redis

try:
    redis_client = redis.StrictRedis(host='localhost', port=6390, db=0)
except Exception as e:
    print(f"Error connecting to Redis: {e}")

