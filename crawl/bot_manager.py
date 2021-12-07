import concurrent.futures
import json
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep

from config.config import Config
from crawl.divar.token import CrawlToken
from crawl.rabbit import TokenWaitPost
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
        if self.cities:
            with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(self.run_city, c) for c in self.cities]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        message = future.result()
                        if message is not None:
                            logging.info("TokenManager get token")
                            print('result', True)
                    except Exception as e:
                        logging.error(e)
                        print(e)
        else:
            sleep(30)


class PostManager:
    def __init__(self):
        self.crawler = CrawlPost()

    def callback(self, ch, method, properties, body):
        token = body.decode()
        res = self.crawler.get_post(token)
        post_rabbit(res)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume_wait_posts(self):
        r = TokenWaitPost()
        r.channel.basic_qos(prefetch_count=1)
        r.channel.basic_consume(queue="divar_wait_posts", on_message_callback=self.callback)
        r.channel.start_consuming()

    def manage(self):
        while True:
            try:
                f_posts = TokenWaitPost().get_len_queue()
                if f_posts > 0:
                    with ThreadPoolExecutor(max_workers=200) as executor:
                        # with ProcessPoolExecutor(max_workers=1) as executor:
                        futures = [executor.submit(self.consume_wait_posts) for c in range(200)]
                        for future in concurrent.futures.as_completed(futures):
                            try:
                                message = future.result()
                                if message is not None:
                                    print('result', message)
                            except Exception as e:
                                print(e)
            except Exception as e:
                print(e)
                sleep(10)
                continue
