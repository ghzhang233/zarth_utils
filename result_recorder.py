import os
import json

from general_utils import get_time_random

dir_results = os.path.join(os.getcwd(), "results")
if not os.path.exists(dir_results):
    os.makedirs(dir_results)


class ResultRecorder:
    def __init__(self, file_name_record=None, initial_record=None):
        self.ending = False

        if file_name_record is None:
            self.file_name_record = "%s.result" % get_time_random()
        else:
            if file_name_record.endswith(".result"):
                self.file_name_record = "%s" % file_name_record
            else:
                self.file_name_record = "%s.result" % file_name_record
        self.file_name_record = os.path.join(dir_results, self.file_name_record)

        self.record = dict()
        if initial_record is not None:
            self.update(initial_record)

    def __getitem__(self, item):
        return self.record[item]

    def __setitem__(self, key, value):
        assert key not in self.record.keys()
        self.record[key] = value

    def update(self, new_record):
        assert not self.ending
        assert type(new_record) == dict
        for k in new_record.keys():
            self.__setitem__(k, new_record[k])

    def dump(self):
        self.ending = True
        with open(self.file_name_record, "w", encoding="utf-8") as fout:
            fout.write(json.dumps(self.record))
            fout.write("\n$END$\n")

    def load(self):
        with open(self.file_name_record, "r", encoding="utf-8") as fin:
            json_record = fin.readline()
            assert fin.readline().strip() == "$END$"
            self.record = json.loads(json_record)

    def show(self, print_fn=print):
        print_fn(json.dumps(self.record, sort_keys=True, indent=4, separators=(',', ': ')))

    def to_dict(self):
        return self.record
