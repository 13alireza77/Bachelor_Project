from time import sleep
import random
import string
from components.requests import TorRequest


class CrawlToken:

    def __init__(self):
        pass

    def get_list_ads(self, time_stamp: int, city):
        url = f"https://api.divar.ir/v8/search/{city['idc']}/{city['category']}"
        jsn = {'json_schema': {'category': {'value': city['category']}},
               'last-post-date': time_stamp}
        if city['has_photo']:
            jsn['json_schema']['category'].update({'has-photo': city})
        if city['urgent']:
            jsn['json_schema']['category'].update({'urgent': city['urgent']})

        return TorRequest.tor_request_post(url=url, jsn=jsn, return_type='json',
                                           cookies={"did": ''.join(
                                               random.choice(string.ascii_lowercase) for i in range(16))})

    def get_tokens(self, jsn):
        tokens = []
        try:
            list_posts = jsn['web_widgets']['post_list']
            for t in list_posts:
                token = t['data']['token']
                tokens.append(token)
            print("token")
            return tokens
        except Exception as e:
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
                    resp = self.get_list_ads(last_post_date, city)
                    if new_database_last_post_date == database_last_post_date:
                        new_database_last_post_date = resp['first_post_date']
                        get_first = True
                    last_post_date = resp['last_post_date']
                    jsons.append(resp)
                    print(last_post_date, database_last_post_date)
                    if last_post_date < 0 or int(last_post_date) < database_last_post_date:
                        break
                    sleep(0.1)
                except Exception as e:
                    print(resp, e)
                    if not get_first:
                        return None
                    continue
            if get_first:
                tokens = list(map(self.get_tokens, jsons))[0]
                return tokens, new_database_last_post_date, city['_id']
        except Exception as e:
            print(resp, e)
            return None
