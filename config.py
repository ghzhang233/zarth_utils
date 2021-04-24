import os
import sys
import json
import argparse

from zarth_utils.general_utils import get_random_time_stamp
from zarth_utils.logger import get_logger

dir_configs = os.path.join(sys.path[0], "configs")
if not os.path.exists(dir_configs):
    os.makedirs(dir_configs)


class Config:
    def __init__(self, filename_default_config="default_config.json",
                 filename_dump="%s.config" % get_random_time_stamp()):
        self.__parameters = {}

        # load from default config file
        self.__parameters.update(json.load(open(filename_default_config, "r", encoding="utf-8")))

        # add argument parser
        parser = argparse.ArgumentParser()
        for name_param in self.__parameters.keys():
            value_param = self.__parameters[name_param]
            if type(value_param) is bool:
                parser.add_argument("--%s" % name_param, action="store_true", default=value_param)
                parser.add_argument("--no-%s" % name_param, dest="%s" % name_param, action="store_false")
            else:
                parser.add_argument("--%s" % name_param, type=type(value_param), default=value_param)
        args = parser.parse_args()
        self.__parameters.update(vars(args))

        filename_dump = "%s.config" % filename_dump if not filename_dump.endswith(".config") else filename_dump
        self.dump(os.path.join(dir_configs, filename_dump))

        self.__logger = get_logger()

    def __getitem__(self, item):
        return self.__parameters[item]

    def to_dict(self):
        return self.__parameters

    def show(self):
        self.__logger.info("\n%s" % json.dumps(self.__parameters, sort_keys=True, indent=4, separators=(',', ': ')))

    def dump(self, path_dump):
        path_dump = "%s.config" % path_dump if not path_dump.endswith(".config") else path_dump
        json.dump(self.__parameters, open(path_dump, "w", encoding="utf-8"))
