import json
import argparse


class Config:
    def __init__(self):
        self.lock = False
        self.parameters = {
        }

    def add_argument_parser(self):
        parser = argparse.ArgumentParser(description='Process some integers.')
        for name_param in self.parameters.keys():
            parser.add_argument("--%s" % name_param, default=self.parameters[name_param])

        args = parser.parse_args()
        self.parameters.update(vars(args))

    def __setitem__(self, key, value):
        if self.lock:
            raise ValueError
        self.parameters[key] = value

    def __getitem__(self, item):
        return self.parameters[item]

    def from_json(self, name_config_file="default_config.json"):
        self.parameters.update(json.load(open(name_config_file, "r", encoding="utf-8")))

    def to_json(self, name_config_file):
        json.dump(self.parameters, open(name_config_file, "w", encoding="utf-8"))

    def to_dict(self):
        return self.parameters

    def block(self):
        self.lock = True
