import logging

from components.requests import TorRequest


class CrawlPost:
    @staticmethod
    def get_post(token):
        try:
            url = f"https://api.divar.ir/v5/posts/{token}"
            resp = TorRequest().get(url=url).json()
            if resp["error"] != 0:
                print("expire")
                logging.info(f"post of {token} expire")
                return -1, token
            return 1, resp
        except Exception as e:
            print(e)
            logging.error(f"{e}")
            return -2, token
