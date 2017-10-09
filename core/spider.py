from itertools import chain

import asyncio
import aiohttp
import feedparser
from mmh3 import hash64
import lxml.html as lxml_parser
from lxml.etree import XMLSyntaxError, ParserError

from core.pipelines import TelegramPipeline
from core.logger import spider_logger as logger
from core.utils import http_errors
from core.utils import find_between
from settings import HEADERS
from settings import SPIDER_CONN_TIMEOUT
from settings import SPIDER_READ_TIMEOUT
from settings import URL_FETCH_RETRIES


class Spider:

    allowed_codes = (200,)

    # aiohttp session
    _session = None
    _connector = None

    # http headers
    headers = HEADERS
    # url fetch retries num
    url_fetch_retries = URL_FETCH_RETRIES

    # timeouts, sec
    conn_timeout = SPIDER_CONN_TIMEOUT
    read_timeout = SPIDER_READ_TIMEOUT

    def __init__(self, loop, urls, seen_feeds):
        self._loop = loop
        self.urls = urls
        self.seen_feeds = seen_feeds

        self._pipe = TelegramPipeline()
        self._setup_session(keepalive_timeout=60)

    def _setup_session(self, keepalive_timeout=60):
        # create HTTP connector
        self._connector = aiohttp.TCPConnector(
            loop=self._loop,
            keepalive_timeout=keepalive_timeout,
            family=2,  # use IPv4 only
            verify_ssl=False,
            limit=0,  # The total number of simultaneous connections.
            force_close=False,
            use_dns_cache=True
        )

        # create HTTP session
        self._session = aiohttp.ClientSession(
            loop=self._loop,
            headers=self.headers,
            conn_timeout=self.conn_timeout,
            read_timeout=self.read_timeout,
            connector=self._connector
        )

    def response_is_valid(self, response):
        if response is not None:
            return response.status in self.allowed_codes

    async def _get_response_with_retries(self, url, params=None,
                                         fetch_retries=3):
        attempt = 0
        while attempt < fetch_retries:
            attempt += 1
            try:  # fetch response
                async with self._session.get(url, params=params,
                                             allow_redirects=False) as response:
                    if self.response_is_valid(response):
                        logger.info(
                            '{}; attempt {}; "{}"'.format(response.status, attempt, response.url.human_repr()))

                        content = await response.read()
                        return content.decode('utf-8')

                    else:
                        logger.warning(
                            '{}; attempt {}; "{}"'.format(response.status, attempt, response.url.human_repr()))

            except http_errors as e:
                logger.error(
                    'attempt: {}; "{}" ({}) "{}"'.format(attempt, e, type(e), url))

            await asyncio.sleep(2)

        else:
            logger.error(
                'all fetch retries were failed; retries: {}; "{}"'.format(fetch_retries, url))

    async def get_feeds(self, url):
        """
        get feed content
        """
        content = await self._get_response_with_retries(
            url=url.url, params=url.params,
            fetch_retries=URL_FETCH_RETRIES
        )
        if content is not None:
            return await self._loop.run_in_executor(
                None, self.get_feeds_from_content, content)

        return []

    @staticmethod
    def hasher(value):
        return hash64(value)[0]

    @staticmethod
    def get_tree(html):
        """get lxml tree"""
        if html:
            try:
                return lxml_parser.fromstring(html)
            except (XMLSyntaxError, TypeError,
                    ParserError, ValueError) as e:
                logger.error('"{}" while getting html tree'.format(e), exc_info=True)

    @staticmethod
    def _strip_spaces(text):
        return ' '.join(text.split())

    def feed_fingerprint(self, feed):
        title = ''.join(feed.title.split())
        return self.hasher(title)

    def _get_feed_details(self, tree, feed):
        feed_details = {}
        details_keys = tree.xpath('.//b/text()')
        for key in details_keys:
            key = key.strip()
            k = '<b>{}</b>'.format(key)
            details = find_between(
                feed, k, '<br')
            details = details.strip(': ')
            details = self._strip_spaces(details)
            if details:
                feed_details.setdefault('details', {})
                feed_details['details'][key] = details

        return feed_details

    def _get_single_feed(self, entry):
        description = entry.summary
        tree = self.get_tree(description)
        if tree is not None:
            details = self._get_feed_details(tree, description)
            description = ' '.join(tree.xpath('.//text()'))
            description = self._strip_spaces(description)
            feed = {
                'url': entry.link.replace('?source=rss', ''),
                'title': entry.title,
                'description': description,
                'published_date': entry.published,
            }
            feed.update(details)

            return feed

    def get_feeds_from_content(self, content):
        items = feedparser.parse(content)
        feeds = []
        for entry in items.entries:
            feed_fingerprint = self.feed_fingerprint(entry)
            if feed_fingerprint not in self.seen_feeds:
                self.seen_feeds.append(feed_fingerprint)
                feed = self._get_single_feed(entry)
                if feed:
                    feed['id'] = feed_fingerprint
                    feeds.append(feed)

        return feeds

    async def crawl_feeds(self, url):
        feeds = await self.get_feeds(url)
        for feed in feeds or []:
            logger.debug(
                'found new "{}" feed: "{}"'.format(url.description, feed['title']))

        return feeds

    async def run(self):
        tasks = []
        for url in self.urls:
            task = asyncio.ensure_future(
                self.crawl_feeds(url),
                loop=self._loop
            )
            tasks.append(task)

        if tasks:
            feeds = await asyncio.gather(*tasks)
            feeds = list(chain(*feeds))
            for feed in feeds:
                self._pipe.process_item(feed)

    def close(self):
        """close session"""
        if self._session is not None:
            self._session.close()
            self._session = None
