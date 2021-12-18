import logging

import requests

from Bachelor_Project.settings import config


class TorRequest(requests.Session):
    host = config.get("postgres", 'host')

    def __init__(self):
        super().__init__()

    def post(self, url, data=None, json=None, **kwargs):
        try:
            self.proxies = {f'http': f'socks5h://{self.host}:9050', 'https': f'socks5h://{self.host}:9050'}
            # self.mount(url, HTTPAdapter(max_retries=3))
            response = self.request('POST', url, data=data, json=json, **kwargs, timeout=20)
            if response.status_code != 200:
                raise Exception
            return response
        except Exception as e:
            logging.error(f"post url:{url} not work,{e}")
            print(e)
            return

    def get(self, url, **kwargs):
        try:
            self.proxies = {f'http': f'socks5h://{self.host}:9050', 'https': f'socks5h://{self.host}:9050'}
            # self.mount(url, HTTPAdapter(max_retries=3,))
            kwargs.setdefault('allow_redirects', True)
            response = self.request('GET', url, **kwargs, timeout=20)
            if response.status_code != 200:
                raise Exception
            return response
        except Exception as e:
            logging.error(f"get url:{url} not work,{e}")
            print(e)
            return
