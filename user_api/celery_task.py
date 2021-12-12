# from celery.decorators import task
import logging

import pandas as pd
from django.apps import apps

from crawl.divar.post import CrawlPost


# @task
def render_xlsx_from_mongo(request_id, static_path, suggestions: list, type="data"):
    try:
        RequestHistory = apps.get_model('user_api', "RequestHistory")
        request_history = RequestHistory.objects.get(request_id=request_id)
    except Exception as e:
        logging.error(e)
        return
    try:
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
        request_history.status = 1
        request_history.save()
        pd_json.to_excel(f"{static_path}/{request_id}.xlsx", index=False, encoding='utf-8')
    except Exception as e:
        logging.error(e)
        request_history.status = 0
        request_history.save()
