import os
from configparser import ConfigParser


class Config:
    _parser = None
    __instance = None

    def __init__(self):
        file_path = f"{os.path.dirname(os.path.abspath(__file__))}/../config.cfg"
        self._parser = ConfigParser(allow_no_value=True)
        self._parser.read(file_path, encoding='utf-8')
        self.__instance = self

    def get(self, section_name, option_name, type=str):
        try:
            opt_selector = {str: self._parser.get, int: self._parser.getint, bool: self._parser.getint,
                            float: self._parser.getfloat}
            return opt_selector[type](section_name, option_name)
        except:
            return None
