# -*- coding: utf-8 -*-
from time import time, mktime
from datetime import datetime
import logging

from mmh3 import hash64
import feedparser
import asyncio
import aiohttp
from aiohttp.resolver import AsyncResolver
import async_timeout

import settings
from aiographite.aiographite import connect
from aiographite.protocol import PlaintextProtocol
from utils import (CookieJar, shutdown_exceptions,
                   http_exceptions)


# set default logger
logger = logging.getLogger(__name__)
# disable warnings
logging.getLogger("aiohttp.client").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)


class Crawler:
    """
    Crawl urls
    get and parse urls from RS manager and post results to redis and rabbit
    """

    # http headers
    headers = settings.HEADERS
    # timeouts, sec
    read_timeout = settings.READ_TIMEOUT
    # url fetch retries num
    url_fetch_retries = settings.URL_FETCH_RETRIES
    # http session
    _session = None
    # carbon
    _graphite_conn = None
    _protocol = PlaintextProtocol()

    def __init__(self, loop, revisit_after,
                 server, port=2003):
        self._loop = loop
        # revisit interval, sec
        self._revisit_after = revisit_after
        # graphite
        self._server = server
        self._port = port
        # initialize aiohttp session
        self.setup_session()

    def setup_session(self):
        """
        create aiohttp connector and session
        use custom resolver and cookies jar object
        """
        dummy_jar = CookieJar(loop=self._loop)
        logger.info('initializing http session')
        nameservers = ['8.8.8.8', '8.8.4.4']
        resolver = AsyncResolver(loop=self._loop, nameservers=nameservers)
        connector = aiohttp.TCPConnector(loop=self._loop,
                                         conn_timeout=10,
                                         family=2,  # use IPv4 only
                                         verify_ssl=False,
                                         force_close=True,
                                         use_dns_cache=True,
                                         resolver=resolver)

        session = aiohttp.ClientSession(loop=self._loop,
                                        cookie_jar=dummy_jar,
                                        headers=self.headers,
                                        connector=connector)
        self._session = session

        return session

    @staticmethod
    def response_is_valid(response):
        return response.status == 200

    async def get_feeds(self, url, filter_name):
        """
        get feed content
        """
        retries_counter = 0
        while retries_counter < self.url_fetch_retries:
            try:  # fetch response
                with async_timeout.timeout(self.read_timeout):
                    async with self._session.get(url,
                                                 allow_redirects=False) as response:
                        if self.response_is_valid(response):
                            content = await response.read()
                            return content.decode('utf-8')
                        else:
                            logger.error('response is invalid for filter: "{}"; '
                                         'status code: {}'.format(filter_name, response.status))

            # except http_exceptions:  # try again
            #     pass

            except Exception as e:
                logger.error('exception "{}" ({}) while requesting "{}"'.format(e, type(e), url))

            retries_counter += 1
            await asyncio.sleep(2)
        else:
            # all retries were failed
            logger.critical('{} retries were failed for "{}"'.format(retries_counter, url))

    @staticmethod
    def hasher(value):
        return hash64(value)[0]

    def _get_unseen_feeds(self, feeds, seen):
        items = feedparser.parse(feeds)
        unseen = []
        for entrie in items.entries:
            _hash = self.hasher(entrie.title)
            if _hash not in seen:
                unseen.append(
                    (entrie.title, entrie.published_parsed)
                )
                seen.add(_hash)
        return unseen

    @staticmethod
    def report(feeds):
        if feeds:
            message = 'new feeds: \n'
            for feed, posted_time in feeds:
                dt = datetime.fromtimestamp(mktime(posted_time))
                title = '\ttitle: "{}"; published: "{}"\n'.format(feed, dt)
                message += title
            logger.info(message)

    async def connect(self):
        self._graphite_conn = await connect(self._server,
                                            self._port,
                                            self._protocol,
                                            loop=self._loop)

    async def send_metric(self, filter_name, metric):
        key = 'upwork.{}'.format(filter_name)
        await self._graphite_conn.send(key, metric, time())

    async def fetcher(self, filter_name, url):
        """fetcher worker"""
        last_fingerprint = None
        seen_feeds = set()
        logger.info('start fetcher for "{}".'.format(filter_name))
        while True:
            try:
                metric = 0
                feeds = await self.get_feeds(url, filter_name)
                if feeds is not None:
                    fingerprint = len(feeds)
                    if last_fingerprint is None:
                        new_feeds = self._get_unseen_feeds(feeds, seen_feeds)
                        last_fingerprint = fingerprint
                    elif fingerprint != last_fingerprint:
                        new_feeds = self._get_unseen_feeds(feeds, seen_feeds)
                        if new_feeds:
                            logger.info('found {} new feeds for "{}"'.format(len(new_feeds), filter_name))
                        self.report(new_feeds)
                        metric = len(new_feeds)
                        last_fingerprint = fingerprint
                    else:
                        logger.debug('content was not changed for "{}"'.format(filter_name))

                await self.send_metric(filter_name, metric)
                await asyncio.sleep(self._revisit_after)

            except shutdown_exceptions:
                break

            except Exception:
                logger.critical('worker exception\n', exc_info=True)

    def run(self, urls):
        self._loop.run_until_complete(
            self.connect()
        )
        for url in urls:
            filter_name = url['filter_name']
            url = url['url']
            asyncio.ensure_future(
                self.fetcher(filter_name, url),
                loop=self._loop)

    def close(self):
        self._session.close()