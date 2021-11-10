import os
import shutil
import json
import stat
from json import JSONDecodeError

import joblib
import pandas as pd
import logging
import git


class ResultRecorder:
    def __init__(self, path_record, initial_record=None, use_git=True):
        """
        Initialize the result recorder. The results will be saved in a temporary file defined by path_record.temp.
        To end recording and transfer the temporary files, self.end_recording() must be called.
        :param path_record: the saving path of the recorded results.
        :type path_record: str
        :param initial_record: a record to be initialize with, usually the config in practice
        :type initial_record: dict
        """
        self.__ending = False
        self.__record = dict()

        self.__path_temp_record = "%s.result.temp" % path_record if not path_record.endswith(".result") \
            else path_record + ".temp"
        self.__path_record = "%s.result" % path_record if not path_record.endswith(".result") \
            else path_record

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
        with open(self.__path_temp_record, "a", encoding="utf-8") as fin:
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
        shutil.move(self.__path_temp_record, self.__path_record)
        os.chmod(self.__path_record, stat.S_IREAD)

    def dump(self, path_dump):
        """
        Dump the result record in the path_dump.
        :param path_dump: the path to dump the result record
        :type path_dump: str
        """
        assert self.__ending
        path_dump = "%s.result" % path_dump if not path_dump.endswith(".result") else path_dump
        assert not os.path.exists(path_dump)
        shutil.copy(self.__path_record, path_dump)

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


def load_result(path_record):
    """
    Load the result based on path_record.
    :param path_record: the path of the record
    :type path_record: str
    :return: the result and whether the result record is ended
    :rtype: dict, bool
    """
    ret = dict()
    with open(path_record, "r", encoding="utf-8") as fin:
        ret["path"] = path_record
        for line in fin.readlines():
            if line.strip() == "$END$":
                return ret, True
            if len(line.strip().split()) == 0:
                continue
            ret.update(json.loads(line))
    return ret, False


def collect_results(dir_results):
    """
    Collect all the ended results in dir_results.
    :param dir_results: the directory of the reuslts to be collected
    :type dir_results: str
    :return: all ended result records
    :rtype: pd.DataFrame
    """
    assert os.path.exists(dir_results)
    path_pickled_results = os.path.join(dir_results, ".pickled_results.jbl")
    if os.path.exists(path_pickled_results):
        data = joblib.load(path_pickled_results)
        already_collect_list = data["path"].values
    else:
        data = pd.DataFrame()
        already_collect_list = []

    updated = False
    for path, dir_list, file_list in os.walk(dir_results):
        for file_name in file_list:
            file_path = os.path.join(path, file_name)
            if not os.path.isdir(file_path) and file_path.endswith(".result"):
                if file_path not in already_collect_list:
                    try:
                        result, ended = load_result(file_path)
                        if ended:
                            print("Collecting %s" % file_path)
                            data = data.append(result, ignore_index=True)
                            updated = True
                    except JSONDecodeError:
                        print("Collection Failed at %s" % file_path)

    if updated:
        joblib.dump(data, path_pickled_results)
    return data


def collect_dead_results(dir_results):
    """
    Collect all un-ended results.
    :param dir_results: the directory of the reuslts to be collected
    :type dir_results: str
    :return: all un-ended result records.
    :rtype: pd.DataFrame
    """
    assert os.path.exists(dir_results)
    data = pd.DataFrame()
    for path, dir_list, file_list in os.walk(dir_results):
        for file_name in file_list:
            path = os.path.join(path, file_name)
            if not os.path.isdir(path) and path.endswith(".result.temp"):
                result, ended = load_result(os.path.join(dir_results, path))
                if not ended:
                    data = data.append(result, ignore_index=True)
    return data
