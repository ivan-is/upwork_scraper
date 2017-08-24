
LOG_LEVEL = 'INFO'
LOG_FILE = 'log/spider.log'
LOG_TO_STDOUT = True

SEEN_FEEDS_PATH = 'seen_feeds.json'

# gooble docs settings
GDOCS_TABLE_NAME = 'jobs keywords'
GDOCS_CREDENTIALS_PATH = 'client_secret.json'

# spider settings
URL_FETCH_RETRIES = 5  # max retries for failed requests
SPIDER_CONN_TIMEOUT = 5  # sec
SPIDER_READ_TIMEOUT = 25  # sec

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:55.0) Gecko/20100101 Firefox/55.0'

HEADERS = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Host': 'www.upwork.com',
    'User-Agent': USER_AGENT
}


# upwork credentials
UPWORK_SECURITY_TOKEN = ''
UPWORK_USER_ID = ''
UPWORK_ORG_UID = ''

# telegram credentials
TELEGRAM_TOKEN = ''
TELEGRAM_CHANNEL = ''


try:
    from local_settings import *
except ImportError:
    pass