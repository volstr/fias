import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


def get_logger(name: str = 'app', level: int = logging.INFO) -> logging.Logger:
    """
    Создать/получить лог.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    file_name = os.path.join(os.getcwd(), 'logs')
    if not os.path.isdir(file_name):
        os.mkdir(file_name)
    file_name = os.path.join(file_name, f'{name}.log')

    log_format = logging.Formatter('%(levelname)-9s %(asctime)s %(message)s')

    if hasattr(logging, 'handlers'):
        log_file_handler = TimedRotatingFileHandler(
            file_name,
            encoding='utf-8',
            interval=1,
            backupCount=5,
            when='midnight')
        log_file_handler.setFormatter(log_format)
        logger.addHandler(log_file_handler)

        log_std_handler = logging.StreamHandler(sys.stdout)
        log_std_handler.setFormatter(log_format)
        logger.addHandler(log_std_handler)

    return logger


import_log = get_logger('import')
