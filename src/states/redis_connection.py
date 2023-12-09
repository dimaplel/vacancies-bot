import logging
from typing import Optional, Union

import redis

class RedisConnection:
    def __init__(self, host: str, user: str, pswd: str):
        self.host = host
        self.user = user
        self.password = pswd
        self.conn: Optional[redis.Redis] = None

    def open(self):
        try:
            logging.info(f"Opening Redis connection for username {self.user}")
            self.connection = redis.Redis(host=self.host, username=self.user, password=self.password)
        except Exception as e:
            logging.error("Error while opening connection in %s: %s" % (self.__class__.__name__, e))

    def close(self):
        try:
            self.conn.close()
            print("Disconnected from Redis")
        except Exception as e:
            logging.error("Error while closing connection in %s: %s" % (self.__class__.__name__, e))

    def get(self, key: str) -> Union[str, bytes, None]:
        try:
            value = self.connection.get(key)
            logging.info(f"Retrieved value for {key} from Redis: {value}")
            return value
        except Exception as e:
            logging.error(f"Error getting value for {key} from Redis: {e}")
            return None

    def set(self, key: str, value: Union[str, bytes, int, float]):
        try:
            self.connection.set(key, value)
            logging.info(f"Set {key} to {value} in Redis")
        except Exception as e:
            logging.error(f"Error setting {key} in Redis: {e}")