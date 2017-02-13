import logging
import os
import logging.handlers
import logging.config
import settings
import aiohttp
from aiohttp.abc import AbstractCookieJar
import asyncio
from concurrent.futures import _base


class CustomFormatter(logging.Formatter):

    default_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s: '
                                          '%(message)s', '%Y-%m-%d %H:%M:%S')

    def __init__(self, formats):
        """ formats is a dict { loglevel : logformat } """
        self.formatters = {}
        datefmt = '%Y-%m-%d %H:%M:%S'
        for loglevel in formats:
            self.formatters[loglevel] = logging.Formatter(formats[loglevel], datefmt)

    def format(self, record):
        formatter = self.formatters.get(record.levelno, self.default_formatter)
        return formatter.format(record)


def setup_logger(log_file=settings.LOG_FILE,
                 level=settings.LOG_LEVEL,
                 stdout=settings.LOG_TO_STDOUT):

    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    error_format = '%(asctime)s %(levelname)s:%(name)s: %(message)s; (%(filename)s:%(lineno)d)'
    formatter = CustomFormatter({logging.CRITICAL: error_format})

    handlers = [
        logging.handlers.RotatingFileHandler(log_file,
                                             encoding='utf8',
                                             maxBytes=100000000,
                                             backupCount=5)
    ]
    if stdout:
        handlers.append(logging.StreamHandler())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.propagate = False

    for h in handlers:
        h.setFormatter(formatter)
        h.setLevel(level)
        root_logger.addHandler(h)


class CookieJar(AbstractCookieJar):

    """Custom class for cookies processing"""

    def __init__(self, loop=None):
        super().__init__(loop=loop)

    def update_cookies(self, cookies, response_url=None):
        pass

    def filter_cookies(self, request_url):
        return None

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def clear(self):
        pass


# ignored http exceptions
http_exceptions = (asyncio.TimeoutError,
                   aiohttp.errors.ClientOSError,
                   aiohttp.errors.ClientResponseError,
                   aiohttp.errors.ClientRequestError,
                   IndexError,  # aiohttp bug: "bytearray index out of range"; example: "http://wineitalyworld.com"
                   aiohttp.errors.ServerDisconnectedError)

shutdown_exceptions = (GeneratorExit,
                       _base.CancelledError,
                       asyncio.CancelledError,
                       asyncio.futures.InvalidStateError)

