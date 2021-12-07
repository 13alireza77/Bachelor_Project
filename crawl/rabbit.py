import json
from datetime import datetime

from components.rabbit import RabbitConnection
from crawl.redisc import CityRedis


class TokenWaitPost(RabbitConnection):
    _route = 'divar_wait_posts'
    _queue_name = 'divar_wait_posts'
    _exchange = 'topic_wait_posts'
    _connection_name = "rabbit"

    @staticmethod
    def token_rabbit(res, city):
        if res:
            tokens, new_database_last_post_date = res
            TokenWaitPost().insert_many_rabbit(tokens)
            city["last_post_date"] = new_database_last_post_date
            city["last_use_datetime"] = datetime.now().timestamp()
            CityRedis().redis.set(city["city"], json.dumps(city))
