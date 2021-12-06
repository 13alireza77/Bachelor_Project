from crawl.divar.city import CrawlCity


def redis_migrate():
    crawl_city = CrawlCity()
    crawl_city.crawl_cities()
    crawl_city.to_redis()
