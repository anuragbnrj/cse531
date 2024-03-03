import logging
import sys


# Global logger
def setup_logger(name):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[PID %(process)d %(processName)s %(asctime)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def log(logger, string):
    logger.info(string)
    sys.stdout.flush()
