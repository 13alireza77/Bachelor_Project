import requests


class TorRequest(requests.Session):
    def __init__(self):
        super().__init__()

    def post(self, url, data=None, json=None, **kwargs):
        try:
            self.proxies = {'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}
            # self.mount(url, HTTPAdapter(max_retries=3))
            response = self.request('POST', url, data=data, json=json, **kwargs)
            if response.status_code != 200:
                raise Exception
            return response
        except Exception as e:
            print(e)
            return

    def get(self, url, **kwargs):
        try:
            self.proxies = {'http': 'socks5h://185.239.104.215:9050', 'https': 'socks5h://185.239.104.215:9050'}
            # self.mount(url, HTTPAdapter(max_retries=3,))
            kwargs.setdefault('allow_redirects', True)
            response = self.request('GET', url, **kwargs)
            if response.status_code != 200:
                raise Exception
            return response
        except Exception as e:
            print(e)
            return
