import redis
import random
import time

try:
    redis_client = redis.StrictRedis(host='localhost', port=6390, db=0)
except Exception as e:
    print(f"Error connecting to Redis: {e}")




while True:
    randint = random.randint(1, 20)
    channel_name = 'share'
    redis_client.publish(channel_name, f'topic{randint}')
    if randint == 10:
        break
    time.sleep(1)
