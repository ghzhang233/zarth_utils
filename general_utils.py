import os
import random
import datetime


def get_random_time_stamp():
    return "%d-%s" % (random.randint(0, 2333), datetime.datetime.now().strftime('%Y.%m.%d-%H.%M.%S'))


def makedir_if_not_exist(name):
    if not os.path.exists(name):
        os.makedirs(name)
