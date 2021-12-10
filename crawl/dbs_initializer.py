import pymongo

from config.config import Config
from crawl.divar.city import CrawlCity


def redis_migrate():
    crawl_city = CrawlCity()
    crawl_city.crawl_cities()
    crawl_city.to_redis()


def mongo_migrate():
    conf = Config()
    db = "divar"
    collections = {"posts": ["token", ]}

    port = int(conf.get('mongo', 'port'))
    host = str(conf.get('mongo', 'host'))
    mongo_usr = str(conf.get('mongo', 'username'))
    mongo_pass = str(conf.get('mongo', 'password'))
    connection = pymongo.MongoClient(f'mongodb://{mongo_usr}:{mongo_pass}@{host}:{port}/',
                                     socketTimeoutMS=60000)
    for k, v in collections.items():
        uniq = True
        for l in v:
            database = connection[db]
            collection = database[k]
            collection.create_index([(i, 1) for i in l], unique=uniq)
            uniq = False


if __name__ == "__main__":
    mongo_migrate()
