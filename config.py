import json
import argparse

from general_utils import get_random_time_stamp
from logger import get_logger


class Config:
    def __init__(self, filename_default_config="default_config.json",
                 filename_dump="%s.config" % get_random_time_stamp()):
        self.__parameters = {}

        # load from default config file
        self.__parameters.update(json.load(open(filename_default_config, "r", encoding="utf-8")))

        # add argument parser
        parser = argparse.ArgumentParser()
        for name_param in self.__parameters.keys():
            parser.add_argument("--%s" % name_param, default=self.__parameters[name_param])
        args = parser.parse_args()
        self.__parameters.update(vars(args))

        filename_dump = "%s.config" % filename_dump if not filename_dump.endswith(".config") else filename_dump
        json.dump(self.__parameters, open(filename_dump, "w", encoding="utf-8"))

        self.__logger = get_logger()

    def __getitem__(self, item):
        return self.__parameters[item]

    def to_dict(self):
        return self.__parameters

    def show(self):
        self.__logger.info("\n%s" % json.dumps(self.__parameters, sort_keys=True, indent=4, separators=(',', ': ')))
