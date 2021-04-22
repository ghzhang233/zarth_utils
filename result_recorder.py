import os
import sys
import json

from general_utils import get_random_time_stamp
from logger import get_logger

dir_results = os.path.join(sys.path[0], "results")
if not os.path.exists(dir_results):
    os.makedirs(dir_results)


class ResultRecorder:
    def __init__(self, filename_record="%s.result" % get_random_time_stamp(), initial_record=None):
        self.__ending = False
        self.__record = dict()

        filename_record = "%s.result" % filename_record if not filename_record.endswith(".result") else filename_record
        self.__file_record = open(os.path.join(dir_results, filename_record), "w", encoding="utf-8")

        if initial_record is not None:
            self.update(initial_record)
        self.__logger = get_logger()

    def __getitem__(self, item):
        return self.__record[item]

    def __setitem__(self, key, value):
        assert not self.__ending
        assert key not in self.__record.keys()
        self.__record[key] = value
        self.__file_record.write(json.dumps({key: value}))

    def update(self, new_record):
        assert type(new_record) == dict
        for k in new_record.keys():
            self.__setitem__(k, new_record[k])

    def add_with_logging(self, key, value, msg=None):
        self.__setitem__(key, value)
        if msg is None:
            self.__logger.info("%s: %s" % (key, str(value)))
        else:
            self.__logger.info(msg % value)

    def end_recording(self):
        self.__ending = True
        self.__file_record.write("\n$END$\n")
        self.__file_record.close()

    def to_dict(self):
        return self.__record

    def show(self):
        self.__logger.info("\n%s" % json.dumps(self.__record, sort_keys=True, indent=4, separators=(',', ': ')))


def load_result(self, filename_record):
    ret = dict()
    with open(filename_record, "r", encoding="utf-8") as fin:
        for line in fin.readlines():
            if line.strip() == "$END$":
                return
            ret.update(json.loads(line))
    get_logger().warn("File Not Ended!")
