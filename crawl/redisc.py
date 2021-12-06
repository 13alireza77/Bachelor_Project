from components.redisc import RedisConnection


class CityRedis(RedisConnection):
    _connection_name = 'redis'
    _db_number: int = 0
