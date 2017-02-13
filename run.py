# -*- coding: utf-8 -*-
import logging
import asyncio
import signal

import settings
from crawler import Crawler
from utils import setup_logger


setup_logger()
logger = logging.getLogger(__name__)


def shutdown_handler(loop):
    """
    handler for proper finishing the futures
    close all connections
    stopping the loop
    """
    tasks = asyncio.Task.all_tasks(loop)
    try:
        loop.stop()
        for t in tasks:
            t.cancel()
    except Exception as e:
        pass


def run_crawler():
    loop = asyncio.get_event_loop()

    urls = settings.URLS
    revisit = settings.REVISIT_AFTER
    graphite_server = settings.CARBON_SERVER
    graphite_port = settings.CARBON_PORT

    crawler = Crawler(revisit_after=revisit,
                      server=graphite_server,
                      port=graphite_port,
                      loop=loop)
    crawler.run(urls)
    loop.add_signal_handler(
        signal.SIGINT, shutdown_handler, loop)
    loop.run_forever()
    loop.close()
    crawler.close()

if __name__ == "__main__":
    run_crawler()
