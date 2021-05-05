import os
import logging
from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist

dir_logs = os.path.join(os.getcwd(), "logs")
makedir_if_not_exist(dir_logs)


def get_logger(filename_log="%s.log" % get_random_time_stamp()):
    ret_logger = logging.getLogger()
    ret_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s', datefmt='%Y-%m-%d-%H:%M:%S')

    if not ret_logger.handlers:
        filename_log = "%s.log" % filename_log if not filename_log.endswith(".log") else filename_log
        fh = logging.FileHandler(os.path.join(dir_logs, filename_log))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        ret_logger.addHandler(ch)
        ret_logger.addHandler(fh)

    return ret_logger
