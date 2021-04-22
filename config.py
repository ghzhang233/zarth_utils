import json
import argparse

from logger import get_logger


class Config:
    def __init__(self, default_config_filename="default_config.json"):
        self.__parameters = {}

        # load from default config file
        self.__parameters.update(json.load(open(default_config_filename, "r", encoding="utf-8")))

        # add argument parser
        parser = argparse.ArgumentParser()
        for name_param in self.__parameters.keys():
            parser.add_argument("--%s" % name_param, default=self.__parameters[name_param])
        args = parser.parse_args()
        self.__parameters.update(vars(args))
        self.logger = get_logger()

    def __getitem__(self, item):
        return self.__parameters[item]

    def to_dict(self):
        return self.__parameters

    def dump(self, filename):
        json.dump(self.__parameters, open(filename, "w", encoding="utf-8"))

    def show(self):
        for key in self.__parameters.keys():
            self.logger.info("%s: %s" % (key, str(self.__parameters[key])))
