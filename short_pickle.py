import pickle
import os
from general_utils import get_time_random

dir_pickled_obj = os.path.join(os.getcwd(), "pickled_objs")
if not os.path.exists(dir_pickled_obj):
    os.makedirs(dir_pickled_obj)


def save(obj, path_file=os.path.join(dir_pickled_obj, "%s.pkl" % get_time_random())):
    if not path_file.endswith("pkl"):
        path_file = path_file + ".pkl"
    pickle.dump(obj, open(path_file, "wb"))


def load(path_file):
    pickle.load(open(path_file, "rb"))
