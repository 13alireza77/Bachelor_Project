import io

# from celery.decorators import task
import os

from crawl.divar.post import CrawlPost
import pandas as pd


# @task
def render_xlsx_from_mongo(request_id, static_path, suggestions: list, type="data"):
    crawl_post = CrawlPost()
    result = []
    if type == "data":
        for token in suggestions:
            status, response = crawl_post.get_post(token)
            if status == 1 and isinstance(response, dict) and "data" in response:
                result.append(response["data"])
        pd_json = pd.json_normalize(result)

    else:
        for token in suggestions:
            status, response = crawl_post.get_post(token)
            if status == 1 and isinstance(response, dict) and "data" in response:
                result.append(response["data"])
        pd_json = pd.DataFrame.from_records(result)

    pd_json.to_excel(f"{static_path}/{request_id}.xlsx", index=False, encoding='utf-8')
