import json
import re
from datetime import datetime

from components.requests import TorRequest
from crawl.redisc import CityRedis


class CrawlCity:
    def __init__(self):
        self.cities = []
        self.lista = [1, 2, 3, 4, 5, 6, 7]
        self.listb = [15, 17, 10, 32, 39, 18, 25, 34, 27, 11, 20, 22, 35, 28, 36, 19, 13, 21, 14, 38, 16, 8, 9, 12]
        self.listc = [24, 851, 775, 869, 853, 824, 825, 793, 748, 663, 802, 846, 870, 842, 794, 819, 29, 859, 872, 830,
                      796, 759, 797, 807, 776, 664, 710, 662, 778, 26, 785, 815, 760, 798, 708, 751, 779, 780, 37, 765,
                      314, 832, 868, 771, 766, 781, 811, 829, 791, 833, 866, 820, 834, 808, 816, 864, 747, 835, 782,
                      871, 803, 799, 772, 839, 767, 809, 805, 23, 783, 752, 874, 822, 777, 745, 800, 817, 826, 706, 867,
                      671, 316, 852, 865, 854, 857, 812, 768, 855, 756, 761, 861, 818, 707, 858, 754, 602, 810, 795,
                      827, 850, 788, 823, 786, 789, 836, 849, 860, 665, 790, 813, 660, 804, 30, 750, 863, 821, 831, 33,
                      806, 848, 749, 847, 743, 746, 787, 828, 862, 856, 840, 873, 837, 762, 763, 814, 317, 773, 843,
                      769, 792, 764, 845, 841, 31, 784, 774, 770, 838, 744, 753, 709, 844, 318]

    torrequest = TorRequest()

    def crawl_cities(self):
        response = self.torrequest.get(url='https://divar.ir/s/tehran').text
        response = re.search(r'window.__PRELOADED_STATE__ = "(.*?)";', response).group(1)
        response = response.replace('\\"', '"')
        response = json.loads(response)
        response = response["city"]["compressedData"]
        for r in response:
            self.cities.append((r[0], r[2], self.grade_city(r[0])))
            if len(r) > 3:
                for k, v in r[3].items():
                    self.cities.append((int(k), v, self.grade_city(k)))

    def to_city_objects(self):
        cities_objects = []
        for c in self.cities:
            cities_objects.append({"city": c[1], "idc": c[0], "grade": c[2], "last_post_date": -1,
                                   "last_use_datetime": datetime.now().timestamp()})
        return cities_objects

    def grade_city(self, idc):
        if idc in self.lista:
            return 1
        elif idc in self.listb:
            return 2
        elif idc in self.listc:
            return 3
        else:
            return 4

    def to_redis(self):
        cities = self.to_city_objects()
        city_redis = CityRedis()
        for c in cities:
            city_redis.redis.zadd("city", {json.dumps(c): c["grade"]})
