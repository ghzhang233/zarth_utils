import random
import datetime


def get_random_time_stamp():
    return "%d-%s" % (random.randint(0, 2333), datetime.datetime.now().strftime('%Y.%m.%d-%H.%M.%S'))
