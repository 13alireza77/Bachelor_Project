from app.models import WaitContact
from components.requests import TorRequest


class CrawlPost:
    def __init__(self):
        pass

    def get_url(self, token: str):
        return f"https://api.divar.ir/v5/posts/{token}"

    def get_post(self, token):
        try:
            url = self.get_url(token)
            resp = TorRequest.tor_request_get(url=url, return_type='json')
            if resp["error"] != 0:
                print("expire")
                return -1, token

            # postT = Post()
            # postO = PostOriginal()
            res = WaitContact().insert_token(token)
            if res != "Exception":
                print("post")
                return 1, resp
                # postO.publish_post(resp)

        except Exception as e:
            print(e)
            return -2, token

    # def consume_wait_post(self):
    #     try:
    #         token_wait_post = TokenWaitPost()
    #         body = token_wait_post.basic_get()
    #         token = body.decode()
    #         self.get_post(token)
    #     except Exception as e:
    #         print(e)
