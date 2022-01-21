import json
import logging

from django.apps import apps

from crawl.divar.post import CrawlPost
from crawl.formatter import PostFormater
from crawl.models import PostDb


def render_suggestions_xlsx(request_id, static_path, suggestions: list):
    try:
        RequestHistory = apps.get_model('user_api', "RequestHistory")
        request_history = RequestHistory.objects.get(request_id=request_id)
    except Exception as e:
        logging.error(e)
        return
    try:
        crawl_post = CrawlPost()
        result = []
        for token in suggestions:
            status, response = crawl_post.get_post(token)
            if status == 1 and isinstance(response, dict) and "data" in response:
                result.append(PostFormater(response).clean())
        request_history.status = 1
        request_history.save()
        with open(f"{static_path}/{request_id}.json", 'w') as fout:
            json.dump(result, fout, default=str)
    except Exception as e:
        logging.error(e)
        request_history.status = 0
        request_history.save()


def render_datas(request_id, static_path, from_date, to_date, user, page: int, page_count: int, categories=None,
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
    result = [(r, r.pop('_id'))[0] for r in result[page * page_count + 1:(page + 1) * page_count]]
    try:
        request_history.status = 1
        request_history.count_data = len(result)
        request_history.save()
        AccessLevel.objects.get(user=user).update_max_number_of_data(len(result))
        with open(f"{static_path}/{request_id}.json", 'w') as fout:
            json.dump(result, fout, default=str)
    except Exception as e:
        logging.error(e)
        request_history.status = 0
        request_history.save()
