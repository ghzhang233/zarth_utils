import pickle
import os
from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist

dir_pickled_obj = os.path.join(os.getcwd(), "pickled_objs")
makedir_if_not_exist(dir_pickled_obj)


def save(obj, path_file=os.path.join(dir_pickled_obj, "%s.pkl" % get_random_time_stamp())):
    if not path_file.endswith("pkl"):
        path_file = path_file + ".pkl"
    pickle.dump(obj, open(path_file, "wb"))


def load(path_file):
    pickle.load(open(path_file, "rb"))
