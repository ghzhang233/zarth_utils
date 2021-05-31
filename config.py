import os
import json
import argparse
import logging

from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist

dir_configs = os.path.join(os.getcwd(), "configs")


class Config:
    def __init__(self,
                 default_config_dict=None,
                 default_config_file=os.path.join(os.getcwd(), "default_config.json")):
        self.__parameters = {}

        # load from default config file
        if default_config_dict is not None:
            self.__parameters.update(default_config_dict)
        else:
            self.__parameters.update(json.load(open(default_config_file, "r", encoding="utf-8")))

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

    def __getitem__(self, item):
        return self.__parameters[item]

    def to_dict(self):
        return self.__parameters

    def show(self):
        logging.info("\n%s" % json.dumps(self.__parameters, sort_keys=True, indent=4, separators=(',', ': ')))

    def dump(self, path_dump=None):
        if path_dump is None:
            makedir_if_not_exist(dir_configs)
            path_dump = os.path.join(dir_configs, "%s.config" % get_random_time_stamp())
        path_dump = "%s.config" % path_dump if not path_dump.endswith(".config") else path_dump
        json.dump(self.__parameters, open(path_dump, "w", encoding="utf-8"))
