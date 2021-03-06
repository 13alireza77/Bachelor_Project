import itertools
import logging
import random
import string
from time import sleep

from components.requests import TorRequest


class CrawlToken:

    def __init__(self):
        pass

    def get_list_ads(self, time_stamp: int, city_id):
        url = f"https://api.divar.ir/v8/search/{city_id}/ROOT"
        jsn = {
            "json_schema": {
                "category": {
                    "value": "ROOT"
                }
            },
            "last-post-date": time_stamp
        }

        cookies = {"did": ''.join(random.choice(string.ascii_lowercase) for _ in range(16))}
        return TorRequest().post(url=url, json=jsn, cookies=cookies).json()

    def get_tokens(self, jsn):
        tokens = []
        try:
            list_posts = jsn['web_widgets']['post_list']
            for t in list_posts:
                token = t['data']['token']
                tokens.append(token)
            return tokens
        except Exception as e:
            logging.error(f"{e}")
            print(e)
            return tokens

    def crawl_token(self, city):
        resp = None
        try:
            jsons = []
            database_last_post_date = int(city['last_post_date'])
            new_database_last_post_date = database_last_post_date
            last_post_date = 0
            get_first = False
            while True:
                try:
                    resp = self.get_list_ads(last_post_date, city["idc"])
                    if new_database_last_post_date == database_last_post_date:
                        new_database_last_post_date = resp['first_post_date']
                        get_first = True
                    last_post_date = resp['last_post_date']
                    jsons.append(resp)
                    logging.info(
                        f"{city['city']} CrawlToken last_post_date:{last_post_date}|database_last_post_date:{database_last_post_date}")
                    print(city['city'], last_post_date, database_last_post_date)
                    if last_post_date < 0 or int(last_post_date) < database_last_post_date:
                        break
                    sleep(0.1)
                except Exception as e:
                    logging.error(f"{resp}, {e}")
                    print(resp, e)
                    if not get_first:
                        return None
                    continue
            if get_first:
                tokens = list(itertools.chain(*map(self.get_tokens, jsons)))
                return tokens, new_database_last_post_date
        except Exception as e:
            logging.error(f"{resp}, {e}")
            print(resp, e)
            return None
