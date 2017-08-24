import os
import logging
from logging.handlers import RotatingFileHandler

from settings import LOG_FILE, LOG_LEVEL, LOG_TO_STDOUT


def setup_logger(log_file=LOG_FILE,
                 level=LOG_LEVEL,
                 stdout=LOG_TO_STDOUT):
    handlers = []
    formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s: '
                                  '%(message)s', '%Y-%m-%d %H:%M:%S')

    if log_file:
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        file_handler = RotatingFileHandler(log_file,
                                           encoding='utf8',
                                           maxBytes=100000000,
                                           backupCount=5)
        handlers.append(file_handler)

    if stdout:
        handlers.append(logging.StreamHandler())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.propagate = False

    for h in handlers:
        h.setFormatter(formatter)
        h.setLevel(level)
        root_logger.addHandler(h)

# disable debug messages
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


main_logger = logging.getLogger('main')
spider_logger = logging.getLogger('spider')
pipe_logger = logging.getLogger('pipe')
