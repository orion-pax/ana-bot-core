import os
import redis

class RedisHelper():

    def __init__(self):
        try:
            host = os.environ.get("REDIS_HOST")
            port = os.environ.get("REDIS_PORT")
            self.redis_client = redis.StrictRedis(host=host, port=port, db=1, encoding="utf-8", decode_responses=True)
        except Exception as err:
            print(err)

    def set_data(self, name, value):
        response = self.redis_client.set(name, value)
        return response
