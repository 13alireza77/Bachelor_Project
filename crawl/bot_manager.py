import concurrent.futures
import json
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep

from config.config import Config
from crawl.divar.post import CrawlPost
from crawl.divar.token import CrawlToken
from crawl.formatter import PostFormater
from crawl.models import PostDb
from crawl.rabbit import TokenWaitPost, TokenPostException, TokenExpire
from crawl.redisc import CityRedis


class BaseCrawlManager:
    pass


class TokenManager:
    _connection_name = "token_crawler"

    def __init__(self):
        config = Config()
        conf_cities = config.get(self._connection_name, 'cities')
        self.cities = self.get_cities(conf_cities=conf_cities)

    def get_cities(self, conf_cities):
        if conf_cities:
            redis_cities = None
            try:
                redis_cities = conf_cities.strip('"').split(',')
                return [json.loads(CityRedis().redis.get(c)) for c in redis_cities]
            except:
                logging.error(f"redis_cities: {redis_cities}    not valid")
        logging.error("cities not set")
        return None

    @staticmethod
    def run_city(city):
        if city:
            print(city["city"])
            logging.info(f"city:{city['city']} start get token")
            crawler = CrawlToken()
            res = crawler.crawl_token(city)
            TokenWaitPost.token_rabbit(res, city)

    def manage(self):
        while True:
            if self.cities:
                with concurrent.futures.ProcessPoolExecutor(max_workers=len(self.cities)) as executor:
                    futures = [executor.submit(self.run_city, c) for c in self.cities]
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            message = future.result()
                            if message is not None:
                                logging.info("TokenManager get token")
                                print('result', True)
                        except Exception as e:
                            logging.error(f"{e}")
                            print(e)
            else:
                sleep(60)
            sleep(0.1)


class PostManager:
    def __init__(self):
        self.crawler = CrawlPost()

    def manage_post(self, body):
        if body:
            status, mess = body
            if status == -1:
                TokenExpire().publish_token(mess)
            elif status == -2:
                TokenPostException().push(mess)
            elif status == 1:
                return PostFormater(mess).clean()

    def callback(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        token = body.decode()
        res = self.crawler.get_post(token)
        self.manage_post(res)

    def consume_wait_posts(self):
        r = TokenWaitPost()
        r.channel.basic_qos(prefetch_count=1)
        r.channel.basic_consume(queue="divar_wait_posts", on_message_callback=self.callback)
        r.channel.start_consuming()

    def consume_wait_post(self):
        temp = []
        token_wait_post = TokenWaitPost()
        for _ in range(50):
            try:
                body = token_wait_post.basic_get()
                token = body.decode()
                res = self.crawler.get_post(token)
                post = self.manage_post(res)
                if post:
                    temp.append(post)
            except Exception as e:
                print(e)
                logging.error(f"{e}")
                break
        return temp

    def manage(self):
        while True:
            try:
                f_posts = TokenWaitPost().get_len_queue()
                if f_posts > 0:
                    with ThreadPoolExecutor(max_workers=200) as executor:
                        futures = [executor.submit(self.consume_wait_post) for _ in range(100)]
                        postdb = PostDb()
                        for future in concurrent.futures.as_completed(futures):
                            try:
                                message = future.result()
                                postdb.insert_many_ignore_duplicate(message)
                                if message is not None:
                                    print('len_result', len(message))
                                    logging.info(f"len_result, {len(message)}")
                            except Exception as e:
                                print(e)
                                logging.error(f"{e}")
            except Exception as e:
                print(e)
                logging.error(f"{e}")
                sleep(60)
                continue
            sleep(0.1)
