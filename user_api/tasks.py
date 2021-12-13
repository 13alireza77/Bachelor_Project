import logging

import pandas as pd
from django.apps import apps

from crawl.divar.post import CrawlPost
from crawl.models import PostDb


def render_suggestions_xlsx(request_id, static_path, suggestions: list, types="data"):
    try:
        RequestHistory = apps.get_model('user_api', "RequestHistory")
        request_history = RequestHistory.objects.get(request_id=request_id)
    except Exception as e:
        logging.error(e)
        return
    try:
        crawl_post = CrawlPost()
        result = []
        if types == "data":
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


def render_datas_xlsx(request_id, static_path, from_date, to_date, categories=None, city=None, title=None,
                      types="data"):
    try:
        RequestHistory = apps.get_model('user_api', "RequestHistory")
        request_history = RequestHistory.objects.get(request_id=request_id)
    except Exception as e:
        logging.error(e)
        return
    postdb = PostDb()
    query = {}

    query["date"] = {'$gte': from_date, '$lt': to_date}
    if categories:
        query["categories"] = {'$all': [f'/.*{c}.*/' for c in categories]}
    if city:
        query["city"] = city
    if title:
        query["title"] = f"/.*{title}.*/"
    result = postdb.find(query)
    try:
        if types == "data":
            pd_json = pd.json_normalize(result)
        else:
            pd_json = pd.DataFrame.from_records(result)
        request_history.status = 1
        request_history.save()
        pd_json.to_excel(f"{static_path}/{request_id}.xlsx", index=False, encoding='utf-8')
    except Exception as e:
        logging.error(e)
        request_history.status = 0
        request_history.save()
