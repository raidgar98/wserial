import os
import sys
import logging

LOG_LEVEL = logging.DEBUG if 'DEBUG' in os.environ else logging.INFO
LOG_FORMAT = "[%(levelname)s][%(asctime)-15s][%(name)s] %(message)s"

def get_logger(*, module_name : str):
    logger = logging.getLogger(module_name)
    logger.setLevel(LOG_LEVEL)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(LOG_LEVEL)
    ch.setFormatter(logging.Formatter(LOG_FORMAT))

    if not logger.hasHandlers():
        logger.addHandler(ch)

    return logger
