import datetime
import logging
import re

from unidecode import unidecode


class BaseFormatter:
    def __init__(self):
        pass

    def _extract_mentions(self, text):
        return list(set(re.findall('@([\w_.]+)', text)))

    def _extract_hashtags(self, text):
        return list(set(re.findall('#([\w_]+)', text)))

    def _extract_emails(self, text):
        return list(set(re.findall(
            '[\w\-\.]+@[\w-]+\.+[\w-]{2,10}', text)))

    def _extract_entity(self, text):
        result = {}
        # result['lf_emails'] = self.extract_emails(text)
        result['lf_hashtags'] = self._extract_hashtags(text)
        result['lf_mentions'] = self._extract_mentions(text)
        return result

    def _remove_keys(self, d, remove_keys: list = None, parent_key=''):
        if remove_keys is None:
            return d
        res = {}
        for k, v in d.items():
            if isinstance(v, bytes):
                continue
            if (parent_key + k) in remove_keys:
                continue
            if isinstance(v, list):
                if len(v) > 0:
                    resultList = []
                    for i in v:
                        if isinstance(i, dict):
                            resultList.append(self._remove_keys(i, remove_keys, parent_key + k + '.'))
                        else:
                            resultList.append(i)
                    res[k] = resultList

            elif isinstance(v, dict):
                nested = self._remove_keys(v, remove_keys, parent_key + k + '.')
                res[k] = nested
            else:
                res[k] = v
        return res

    def _clean_empty(self, d):
        clean = {}
        for k, v in d.items():
            if isinstance(v, bytes):
                continue
            if isinstance(v, list):
                if len(v) > 0:
                    resultList = []
                    for i in v:
                        if isinstance(i, dict):
                            resultList.append(self._clean_empty(i))
                        else:
                            resultList.append(i)
                    clean[k] = resultList

            elif isinstance(v, dict):
                nested = self._clean_empty(v)
                if len(nested.keys()) > 0:
                    clean[k] = nested
            elif v is not None and v != '':
                clean[k] = v
        return clean


class PostFormater(BaseFormatter):
    def __init__(self, post):
        super().__init__()
        self.post = post
        self.search_fields = {"date": ["widgets", "header", "date"],
                              "categories": ["widgets", "breadcrumb", "categories"],
                              "city": ["data", "city"],
                              "suggestions": ["widgets", "suggestions", "widget_list"],
                              "title": ["data", "seo"]}

    @staticmethod
    def get_dict_value_from_path(listKeys, jsonData):
        try:
            localData = jsonData.copy()
            for k in listKeys:
                try:
                    localData = localData[int(k)] if k.isdigit() else localData[k]
                except:
                    localData = localData[k]
            return localData
        except:
            return None

    @staticmethod
    def convert_date(strD):
        if strD == "دیروز":
            return datetime.date.today() - datetime.timedelta(days=1)
        elif strD == "پریروز":
            return datetime.date.today() - datetime.timedelta(days=2)
        elif strD == "لحظاتی پیش" or strD == "دقایقی پیش" or strD == "یک ربع پیش" or ("ساعت پیش" in strD):
            return datetime.date.today()
        elif "روز پیش" in strD:
            day = strD.split()[0]
            day = int(unidecode(day))
            return datetime.date.today() - datetime.timedelta(days=day)
        elif strD == "هفته پیش":
            return datetime.date.today() - datetime.timedelta(weeks=1)
        elif "هفته پیش" in strD:
            week = strD.split()[0]
            week = int(unidecode(week))
            return datetime.date.today() - datetime.timedelta(weeks=week)

    def add_important_items(self, jsn_data):
        for k, v in self.search_fields.items():
            try:
                if k == "date":
                    jsn_data[k] = self.convert_date(jsn_data["widgets"]["header"]["date"])
                elif k == "categories":
                    jsn_data[k] = []
                    categories = jsn_data["widgets"]["breadcrumb"]["categories"]
                    for dict in categories:
                        jsn_data[k].append(dict.get("title"))
                        jsn_data[k].append(dict.get("second_slug"))
                        jsn_data[k].append(dict.get("slug"))
                    jsn_data[k] = '|'.join(jsn_data[k])
                elif k == "city":
                    jsn_data[k] = jsn_data["data"]["city"]
                elif k == "suggestions":
                    jsn_data[k] = []
                    suggestions = jsn_data["widgets"]["suggestions"]["widget_list"]
                    for dict in suggestions:
                        jsn_data[k].extend(dict["data"]["items"][0]["action"]["payload"]["suggested_tokens"])
                elif k == "title":
                    jsn_data[k] = jsn_data["data"]["seo"]["title"]
            except Exception as e:
                logging.error(f"{e}")
                print(e)
                continue

    def clean(self):
        clean_data = self._clean_empty(self.post)
        self.add_important_items(clean_data)
        return clean_data
