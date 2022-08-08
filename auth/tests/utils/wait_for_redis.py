import time
from redis import Redis
import os

redis = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")))

while not redis.ping():
    time.sleep(3)

print("Ok REDIS")
