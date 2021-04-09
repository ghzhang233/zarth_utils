import os
import logging
from general_utils import get_random_time_stamp

dir_logs = os.path.join(os.getcwd(), "logs")
if not os.path.exists(dir_logs):
    os.makedirs(dir_logs)


def get_logger(file_log=os.path.join(dir_logs, "%s.log" % get_random_time_stamp())):
    ret_logger = logging.getLogger()
    ret_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    fh = logging.FileHandler(file_log)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    ret_logger.addHandler(ch)
    ret_logger.addHandler(fh)
    return ret_logger
