from collections import namedtuple

import asyncio
from aiohttp.client_exceptions import ClientConnectionError
from aiohttp.client_exceptions import ClientOSError
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.client_exceptions import ServerTimeoutError
from aiohttp.client_exceptions import ServerConnectionError
from aiohttp.client_exceptions import ServerDisconnectedError

from settings import UPWORK_SECURITY_TOKEN
from settings import UPWORK_USER_ID
from settings import UPWORK_ORG_UID


URL = namedtuple('UpworkURL', ['url', 'description', 'params'])


class URLBuilder:

    url = 'https://www.upwork.com/ab/feed/jobs/rss'

    def __init__(self, keywords):
        self.kws = keywords

    def query_params(self, keywords):
        terms = ' '.join(keywords)
        sq = ' OR '.join(keywords)
        return {
            'api_params': '1',
            'sort': 'renew_time_int+desc',
            'orgUid': UPWORK_ORG_UID,
            'or_terms': terms,
            'q': '({})'.format(sq),
            'securityToken': UPWORK_SECURITY_TOKEN,
            'userUid': UPWORK_USER_ID
        }

    @property
    def urls(self):
        for descr, kws in self.kws.items():
            params = self.query_params(kws)
            yield URL(url=self.url,
                      params=params,
                      description=descr)


http_errors = (
    asyncio.TimeoutError,
    ClientConnectionError,
    ClientOSError,
    ClientResponseError,
    ServerTimeoutError,
    ServerConnectionError,
    ServerDisconnectedError
)


def find_between(s, first, last, offset=0):
    try:
        start = s.index(first, offset) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

