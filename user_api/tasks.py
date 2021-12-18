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


def render_datas_xlsx(request_id, static_path, from_date, to_date, user, page: int, page_count: int, categories=None,
                      city=None,
                      title=None,
                      types="data"):
    try:
        RequestHistory = apps.get_model('user_api', "RequestHistory")
        AccessLevel = apps.get_model('user_api', "AccessLevel")
        request_history = RequestHistory.objects.get(request_id=request_id)
    except Exception as e:
        logging.error(e)
        return
    postdb = PostDb()
    query = {}
    query["date"] = {'$gte': from_date, '$lte': to_date}
    if categories:
        query["categories"] = {'$regex': ''.join([f"{c}|" for c in categories])[:-1]}
    if city:
        query["city"] = {'$regex': f"{city}"}
    if title:
        query["title"] = {'$regex': f"{title}"}
    result = postdb.find(query)
    result = [r for r in result[page * page_count + 1:(page + 1) * page_count]]
    try:
        if types == "data":
            pd_json = pd.json_normalize(result)
        else:
            pd_json = pd.DataFrame.from_records(result)
        request_history.status = 1
        request_history.count_data = len(pd_json.index)
        request_history.save()
        AccessLevel.objects.get(user=user).update_max_number_of_data(len(pd_json.index))
        pd_json.to_excel(f"{static_path}/{request_id}.xlsx", index=False, encoding='utf-8')
    except Exception as e:
        logging.error(e)
        request_history.status = 0
        request_history.save()
