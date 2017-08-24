from time import sleep
from pprint import PrettyPrinter
from telebot import TeleBot

from settings import TELEGRAM_TOKEN
from settings import TELEGRAM_CHANNEL
from core.logger import pipe_logger as logger


class BasePipeline:

    def __init__(self):
        self.pp = PrettyPrinter(indent=4)

    def process_item(self, item):
        if item:
            self.pp.pprint(item)


class TelegramPipeline:

    template = "Title: {title}\n" \
               "Summary: {description}\n" \
               "Date: {date}\n" \
               "URL: {url}\n" \
               "Details: {details}\n"

    def __init__(self):
        self.bot = TeleBot(TELEGRAM_TOKEN)
        self.channel = TELEGRAM_CHANNEL

    def process_item(self, item):
        if item:
            message = self.template.format(title=item['title'],
                                           description=item['description'],
                                           url=item['url'],
                                           date=item['published_date'],
                                           details='no details')
            try:
                self.bot.send_message(self.channel, message)
                sleep(0.5)
            except Exception as e:
                logger.error(e)

#
# template = """
# *{title}*\n
# ```{description}```\n
# *{date}*\n
# """
#
# item = {   'description': 'Need a website that will have three related databases: '
#                    'User Database=&gt;Basic u...',
#     'details': {   'Category': 'Web, Mobile &amp; Software Dev &gt; Web '
#                                'Developmen...',
#                    'Country': 'United States...',
#                    'Posted On': 'August 24, 2017 16:11 UTC...',
#                    'Skills': 'MySQL Administration, PHP, Website '
#                              'Development...'},
#     'id': -6525604513296239443,
#     'published_date': 'Thu, 24 Aug 2017 15:50:13 +0000',
#     'title': 'Back-end and Front page development - Upwork',
#     'url': 'https://www.upwork.com/jobs/Back-end-and-Front-page-development_%7E015ce6dcf18cb60465'}
#
# m = template.format(title=item['title'],
#                     description=item['description'],
#                     date=item['published_date'])
#
# from telebot import types
# markup = types.InlineKeyboardMarkup(row_width=2)
# itembtn1 = types.InlineKeyboardButton('a')
# itembtn2 = types.InlineKeyboardButton('v')
# # itembtn3 = types.KeyboardButton('d')
# markup.add(itembtn1, itembtn2)
#
# bot = TeleBot(TELEGRAM_TOKEN)
# bot.send_message(TELEGRAM_CHANNEL, item)
