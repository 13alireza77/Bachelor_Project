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
            print(city["city"], city)
            CityRedis().redis.set(city["city"], json.dumps(city))


class TokenPostException(RabbitConnection):
    _connection_name = 'rabbit'
    _route = 'divar_posts_Exceptions'
    _queue_name = 'divar_posts_Exceptions'
    _exchange = 'topic_posts_Exceptions'


class TokenExpire(RabbitConnection):
    _connection_name = 'rabbit'
    _route = 'divar_expires'
    _queue_name = 'divar_expires'
    _exchange = 'topic_expires'

    def format_expire(self, token):
        return {"token": token, "deleted": True}

    def publish_token(self, token):
        self.push(data=self.format_expire(token))
