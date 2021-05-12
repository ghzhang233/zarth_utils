import os
import shutil
import sys
import json
import pandas as pd

from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist
from zarth_utils.logger import get_logger

dir_results = os.path.join(os.getcwd(), "results")
makedir_if_not_exist(dir_results)


class ResultRecorder:
    def __init__(self, filename_record="%s.result" % get_random_time_stamp(), initial_record=None):
        self.__ending = False
        self.__record = dict()

        self.__filename_temp_record = "%s.result.temp" % filename_record if not filename_record.endswith(".result") \
            else filename_record
        self.__filename_record = "%s.result" % filename_record if not filename_record.endswith(".result") \
            else filename_record

        if initial_record is not None:
            self.update(initial_record)
        self.__logger = get_logger()

    def write_record(self, line):
        with open(os.path.join(dir_results, self.__filename_temp_record), "a", encoding="utf-8") as fin:
            fin.write(line + "\n")

    def __getitem__(self, item):
        return self.__record[item]

    def __setitem__(self, key, value):
        assert not self.__ending
        assert key not in self.__record.keys()
        self.__record[key] = value
        self.write_record(json.dumps({key: value}))

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
        self.write_record("\n$END$\n")
        shutil.move(os.path.join(dir_results, self.__filename_temp_record),
                    os.path.join(dir_results, self.__filename_record))

    def to_dict(self):
        return self.__record

    def show(self):
        self.__logger.info("\n%s" % json.dumps(self.__record, sort_keys=True, indent=4, separators=(',', ': ')))


def load_result(filename_record):
    ret = dict()
    with open(filename_record, "r", encoding="utf-8") as fin:
        ret["filename"] = filename_record
        for line in fin.readlines():
            if line.strip() == "$END$":
                return ret
            if len(line.strip().split()) == 0:
                continue
            ret.update(json.loads(line))
    get_logger().warn("File \"%s\" Not Ended!" % filename_record)
    return None


def collect_results():
    data = pd.DataFrame()
    for filename in os.listdir(dir_results):
        if not os.path.isdir(filename) and filename.endswith(".result"):
            result = load_result(os.path.join(dir_results, filename))
            if result is not None:
                data = data.append(result, ignore_index=True)
    return data
