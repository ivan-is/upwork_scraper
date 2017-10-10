import os
import json
import asyncio

from core.spider import Spider
from core.gdocs import GDocs
from core.logger import setup_logger
from core.logger import main_logger as logger
from core.utils import URLBuilder
from settings import SEEN_FEEDS_PATH


setup_logger()


def main():
    doc = GDocs()
    try:
        doc.connect()
        kws = doc.jobs_keywords()

    except Exception as e:
        logger.critical(
            '"{}" while getting keywords from google docs. Exiting'.format(e), exc_info=True)

    else:
        if not kws:
            logger.error('no keywords were found. Nothing to do. Exiting')
            return

        logger.debug('found keywords: "{}"'.format(kws))

        builder = URLBuilder(kws)
        loop = asyncio.get_event_loop()

        # extract seen feeds from json
        if os.path.isfile(SEEN_FEEDS_PATH):
            with open(SEEN_FEEDS_PATH) as f:
                seen_feeds = json.load(f)
        else:
            seen_feeds = []

        spider = Spider(urls=builder.urls,
                        loop=loop,
                        seen_feeds=seen_feeds)

        loop.run_until_complete(
            spider.run()
        )
        spider.close()
        loop.close()

        with open(SEEN_FEEDS_PATH, 'w') as f:
            json.dump(spider.seen_feeds, f)


if __name__ == "__main__":
    logger.info('start crawling')
    main()
    logger.info('stop crawling')
