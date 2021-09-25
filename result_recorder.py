import os
import shutil
import json
import stat

import joblib
import pandas as pd
import logging
import git

from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist

dir_results = os.path.join(os.getcwd(), "results")
makedir_if_not_exist(dir_results)


class ResultRecorder:
    def __init__(self, filename_record="%s.result" % get_random_time_stamp(), initial_record=None, use_git=True):
        """
        Initialize the result recorder. The results will be saved in a temporary file defined by filename_record.temp.
        To end recording and tranfer the temporary files, self.end_recording() must be called.
        :param filename_record: the saving path of the recorded results.
        :type filename_record: str
        :param initial_record: a record to be initialize with, usually the config in practice
        :type initial_record: dict
        """
        self.__ending = False
        self.__record = dict()

        self.__filename_temp_record = "%s.result.temp" % filename_record if not filename_record.endswith(".result") \
            else filename_record + ".temp"
        self.__filename_record = "%s.result" % filename_record if not filename_record.endswith(".result") \
            else filename_record

        if initial_record is not None:
            self.update(initial_record)

        if use_git:
            repo = git.Repo(path=os.getcwd())
            assert not repo.is_dirty()
            self.__setitem__("git_commit", repo.head.object.hexsha)

    def write_record(self, line):
        """
        Add a line to the recorded result file.
        :param line: the content to be write
        :type line: str
        """
        with open(os.path.join(dir_results, self.__filename_temp_record), "a", encoding="utf-8") as fin:
            fin.write(line + "\n")

    def __getitem__(self, key):
        """
        Return the item based on the key.
        :param key:
        :type key:
        :return: results[key]
        """
        return self.__record[key]

    def __setitem__(self, key, value):
        """
        Set result[key] = value
        """
        assert not self.__ending
        assert key not in self.__record.keys()
        self.__record[key] = value
        self.write_record(json.dumps({key: value}))

    def update(self, new_record):
        """
        Update the results from new_record.
        :param new_record: the new results dict
        :type new_record: dict
        """
        assert type(new_record) == dict
        for k in new_record.keys():
            self.__setitem__(k, new_record[k])

    def add_with_logging(self, key, value, msg=None):
        """
        Add an item to results and also print with logging. The format of logging can be defined.
        :param key: the key
        :type key: str
        :param value: the value to be added to the results
        :param msg: the message to the logger, format can be added. e.g. msg="Training set %s=%.4lf."
        :type msg: str
        :return:
        :rtype:
        """
        self.__setitem__(key, value)
        if msg is None:
            logging.info("%s: %s" % (key, str(value)))
        else:
            logging.info(msg % value)

    def end_recording(self):
        """
        End the recording. This function will remove the .temp suffix of the recording file and add an END signal.
        :return:
        :rtype:
        """
        self.__ending = True
        self.write_record("\n$END$\n")
        shutil.move(os.path.join(dir_results, self.__filename_temp_record),
                    os.path.join(dir_results, self.__filename_record))
        os.chmod(os.path.join(dir_results, self.__filename_record), stat.S_IREAD)

    def dump(self, path_dump):
        """
        Dump the result record in the path_dump.
        :param path_dump: the path to dump the result record
        :type path_dump: str
        """
        assert self.__ending
        path_dump = "%s.result" % path_dump if not path_dump.endswith(".result") else path_dump
        shutil.copy(os.path.join(dir_results, self.__filename_record), path_dump)

    def to_dict(self):
        """
        Return the results as a dict.
        :return: the results
        :rtype: dict
        """
        return self.__record

    def show(self):
        """
        To show the reuslts in logger.
        """
        logging.info("\n%s" % json.dumps(self.__record, sort_keys=True, indent=4, separators=(',', ': ')))


def load_result(filename_record):
    """
    Load the result based on filename_record.
    :param filename_record: the filename of the record
    :type filename_record: str
    :return: the result and whether the result record is ended
    :rtype: dict, bool
    """
    ret = dict()
    with open(filename_record, "r", encoding="utf-8") as fin:
        ret["filename"] = filename_record
        for line in fin.readlines():
            if line.strip() == "$END$":
                return ret, True
            if len(line.strip().split()) == 0:
                continue
            ret.update(json.loads(line))
    return ret, False


def collect_results():
    """
    Collect all the ended results.
    :return: all ended result records
    :rtype: pd.DataFrame
    """
    path_pickled_results = os.path.join(dir_results, "pickled_results.jbl")
    if os.path.exists(path_pickled_results):
        data = joblib.load(path_pickled_results)
        already_collect_list = data["filename"].values
    else:
        data = pd.DataFrame()
        already_collect_list = []

    for filename in os.listdir(dir_results):
        if not os.path.isdir(filename) and filename.endswith(".result"):
            if os.path.join(dir_results, filename) not in already_collect_list:
                result, ended = load_result(os.path.join(dir_results, filename))
                if ended:
                    data = data.append(result, ignore_index=True)

    joblib.dump(data, path_pickled_results)
    return data


def collect_dead_results():
    """
    Collect all un-ended results.
    :return: all un-ended result records.
    :rtype: pd.DataFrame
    """
    data = pd.DataFrame()
    for filename in os.listdir(dir_results):
        if not os.path.isdir(filename) and filename.endswith(".result"):
            result, ended = load_result(os.path.join(dir_results, filename))
            if not ended:
                data = data.append(result, ignore_index=True)
    return data["filename"]
