import logging

from crawl.bot_manager import TokenManager

if __name__ == "__main__":
    input_arg = "token"
    logging.info(f"{input_arg}")
    print(input_arg)
    try:
        if input_arg == "post":
            c = PostManager()
            c.manage()
        elif input_arg == "contact":
            c = CrawlContact()
            c.crawl_contact()
        elif input_arg == "city":
            c = CrawlCity()
            c.crawl_cities()
            city_objects = c.to_city_objects()
            City().insert_many(city_objects)
        elif input_arg == "token":
            c = TokenManager()
            c.manage()

    except Exception as e:
        logging.error(f"{e}")
        print(e)
