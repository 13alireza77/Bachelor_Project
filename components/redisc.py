import redis

from config.config import Config


class RedisConnection:
    _connection_name = None
    _db_number = None

    def __init__(self):
        config = Config()
        host = config.get(self._connection_name, 'host')
        port = int(config.get(self._connection_name, 'port'))
        password = config.get(self._connection_name, 'password')
        self.redis = redis.client.Redis(
            connection_pool=redis.BlockingConnectionPool(host=host, port=port, password=password, db=self._db_number))
