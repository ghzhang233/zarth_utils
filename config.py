import os
import json
import argparse
import logging

import yaml

from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist
from zarth_utils.logger import logging_info

dir_configs = os.path.join(os.getcwd(), "configs")


def smart_load(path_file):
    if path_file.endswith("json"):
        return json.load(open(path_file, "r", encoding="utf-8"))
    elif path_file.endswith("yaml"):
        return yaml.safe_load(open(path_file, "r", encoding="utf-8"))
    else:
        logging.warning("Un-identified file type. It will be processed as json by default.")
        return json.load(open(path_file, "r", encoding="utf-8"))


class Config:
    def __init__(self, default_config_file=None, default_config_dict=None, use_argparse=True):
        """
        Initialize the config. Note that either default_config_dict or default_config_file in json format must be
        provided! The keys will be transferred to argument names, and the type will be automatically detected. The
        priority is ``the user specified parameter (if the use_argparse is True)'' > ``user specified config file (if
        the use_argparse is True)'' > ``default config dict'' > ``default config file''.

        Examples:
        default_config_dict = {"lr": 0.01, "optimizer": "sgd", "num_epoch": 30, "use_early_stop": False}
        Then the following corresponding arguments will be added in this function if use_argparse is True:
        parser.add_argument("--lr", type=float)
        parser.add_argument("--optimizer", type=str)
        parser.add_argument("--num_epoch", type=int)
        parser.add_argument("--use_early_stop", action="store_true", default=False)
        parser.add_argument("--no-use_early_stop", dest="use_early_stop", action="store_false")

        :param default_config_dict: the default config dict
        :type default_config_dict: dict
        :param default_config_file: the default config file path
        :type default_config_file: str
        """
        self.__parameters = {}

        # load from default config file
        if default_config_dict is None and default_config_file is None:
            if os.path.exists(os.path.join(os.getcwd(), "default_config.json")):
                default_config_file = os.path.join(os.getcwd(), "default_config.json")
            else:
                logging.error("Either default_config_file or default_config_dict must be provided!")
                raise NotImplementedError

        if default_config_file is not None:
            self.__parameters.update(smart_load(default_config_file))
        if default_config_dict is not None:
            self.__parameters.update(default_config_dict)

        # transform the param terms into argparse
        if use_argparse:
            parser = argparse.ArgumentParser()
            parser.add_argument("--config_file", type=str, default=None)
            # add argument parser
            for name_param in self.__parameters.keys():
                value_param = self.__parameters[name_param]
                if type(value_param) is bool:
                    parser.add_argument("--%s" % name_param, action="store_true", default=value_param)
                    parser.add_argument("--no-%s" % name_param, dest="%s" % name_param, action="store_false")
                elif type(value_param) is list:
                    parser.add_argument("--%s" % name_param, type=type(value_param[0]), default=value_param, nargs="+")
                elif type(value_param) is dict:
                    logging.warning("Nested config term \"%s\" is not supported for automatic argparse!" % name_param)
                    continue
                else:
                    parser.add_argument("--%s" % name_param, type=type(value_param), default=value_param)
            args = parser.parse_args()

            if args.config_file is not None:
                self.__parameters.update(smart_load(args.config_file))

            updated_parameters = dict()
            args_dict = vars(args)
            for k in vars(args):
                if k != "config_file" and self.__parameters[k] != args_dict[k]:
                    updated_parameters[k] = args_dict[k]
            self.__parameters.update(updated_parameters)

        for k in self.__parameters.keys():
            assert k != "__parameters"
            assert k != "__getitem__"
            assert k != "to_dict"
            assert k != "show"
            assert k != "dump"
            assert k != "keys"
            setattr(self, k, self.__parameters[k])

    def __getitem__(self, item):
        """
        Return the config[item]
        :param item: the key of interest
        :type item: str
        :return: config[item]
        """
        return self.__parameters[item]

    def to_dict(self):
        """
        Return the config as a dict
        :return: config dict
        :rtype: dict
        """
        return self.__parameters

    def show(self):
        """
        Show all the configs in logging. If get_logger is used before, then the outputs will also be in the log file.
        """
        logging_info("\n%s" % json.dumps(self.__parameters, sort_keys=True, indent=4, separators=(',', ': ')))

    def dump(self, path_dump=None):
        """
        Dump the config in the path_dump.
        :param path_dump: the path to dump the config
        :type path_dump: str
        """
        if path_dump is None:
            makedir_if_not_exist(dir_configs)
            path_dump = os.path.join(dir_configs, "%s.json" % get_random_time_stamp())
        path_dump = "%s.json" % path_dump if not path_dump.endswith(".json") else path_dump
        assert not os.path.exists(path_dump)
        with open(path_dump, "w", encoding="utf-8") as fout:
            json.dump(self.__parameters, fout)

    def keys(self):
        return self.__parameters.keys()


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, default=None)
    return parser


def parser2config(parser):
    return args2config(parser.parse_args())


def args2config(args):
    args_dict = vars(args)
    return Config(default_config_dict=args_dict, use_argparse=False)


def is_configs_same(config_a, config_b, ignored_keys=("load_epoch",)):
    config_a, config_b = config_a.to_dict(), config_b.to_dict()

    # make sure config A is always equal or longer than config B
    if len(config_a.keys()) < len(config_b.keys()):
        swap_var = config_a
        config_a = config_b
        config_b = swap_var

    if len(config_a.keys() - config_b.keys()) > 1:
        logging.error(
            "Different config numbers: %d (Existing) : %d (New)!" % (len(config_a.keys()), len(config_b.keys())))
        return False
    elif len(config_a.keys() - config_b.keys()) == 1 and (config_a.keys() - config_b.keys())[0] != "config_file":
        logging.error(
            "Different config numbers: %d (Existing) : %d (New)!" % (len(config_a.keys()), len(config_b.keys())))
        return False
    else:
        for i in config_a.keys() & config_b.keys():
            _ai = tuple(config_a[i]) if type(config_a[i]) == list else config_a[i]
            _bi = tuple(config_b[i]) if type(config_b[i]) == list else config_b[i]
            if _ai != _bi and i not in ignored_keys:
                logging.error("Mismatch in %s: %s (Existing) - %s (New)" % (str(i), str(config_a[i]), str(config_b[i])))
                return False

    return True
