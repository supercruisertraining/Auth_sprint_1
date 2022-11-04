import time

from core.config import config

from redis import Redis

if __name__ == '__main__':
    redis = Redis(host=config.REDIS_HOST)
    while True:
        if redis.ping():
            redis.close()
            break
        time.sleep(1)
