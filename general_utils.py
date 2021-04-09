import random
import datetime


def get_time_random():
    return "%s-%d" % (datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'), random.randint(0, 2333))
