import datetime
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
        self.keyPaths = [["data", "category"], ["data", "city"], ["widgets", "description"],
                         ["widgets", "header"], ["widgets", "list_data"],
                         ["widgets", "car_inspection", "demo_inspection", "car_inspection_scores"], ["token"],
                         ["widgets", "breadcrumb"]]

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

    # def get_trans(self, word):
    #     trans_db = Translate()
    #     trans = trans_db.get_translate(word)
    #     if trans == "Exception":
    #         trans = Transelator().transelator(word)["sentences"][0]["trans"]
    #         trans = trans.replace(" ", "_")
    #         trans = trans.lower()
    #         if trans:
    #             trans_db.insert_word(word, trans)
    #     if trans:
    #         return trans
    #     return word

    # def get_int(self, word):
    #     persian_numbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
    #     if type(word) is not str or not any(c in word for c in persian_numbers):
    #         return word
    #     else:
    #         word = persian.convert_fa_numbers(word)
    #         if "تومان" in word:
    #             word = re.sub("\D", "", word)
    #         if word.isnumeric():
    #             return int(word)
    #         return word

    def get_important_items(self, new_jsn, jsn):
        for path in self.keyPaths:
            val = self.get_dict_value_from_path(path, jsn)
            if val:
                # if path[-1] == "list_data":
                #     DicData = {}
                #     for v in val:
                #         if "value" in v:
                #             DicData[self.get_trans(v["title"])] = self.get_int(v["value"])
                #         elif "items" in v:
                #             DicItems = {}
                #             for d in v["items"]:
                #                 if "value" in d:
                #                     DicItems[self.get_trans(d["title"])] = self.get_int(d["value"])
                #                 elif "available" in d:
                #                     DicItems[self.get_trans(d["title"])] = self.get_int(d["available"])
                #             DicData[self.get_trans(v["title"])] = DicItems
                #     new_jsn[path[-1]] = DicData
                # elif path[-1] == "car_inspection_scores":
                #     DictData = {}
                #     for v in val:
                #         if "score_color" in v and "percentage_score" in v:
                #             DictData[self.get_trans(v["title"])] = self.get_int(v["percentage_score"])
                #         elif "score_color" in v and "score_color" in v:
                #             DictData[self.get_trans(v["title"])] = self.get_int(v["score_color"])
                #     new_jsn[path[-1]] = DictData
                if path[-1] == "breadcrumb":
                    ListData = []
                    for d in reversed(val["categories"]):
                        ListData.append(d["second_slug"])
                    val["lf_slugs"] = ' - '.join(ListData)
                    new_jsn[path[-1]] = val
                elif path[-1] == "header":
                    val["date"] = str(self.convert_date(val["date"]))
                    new_jsn[path[-1]] = val
                else:
                    new_jsn[path[-1]] = val
        return new_jsn

    def clean(self):
        result = self._clean_empty(self.post)
        finaljsn = self.get_important_items({}, result)
        return finaljsn

# class ContactFormater(BaseFormatter):
#     def __init__(self, phone, token):
#         super().__init__()
#         self.phone = phone
#         self.token = token
#
#     def contact_for_ads(self):
#         return {
#             "token": self.token,
#             "widgets": {
#                 "contact": {
#                     "phone": self.phone
#                 }
#             }
#         }
#
#     def contact_for_user(self):
#         return {"phone": self.phone}
