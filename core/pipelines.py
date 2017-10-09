import json
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

    SUMMARY_LEN = 100
    DETAILS_LEN = 50
    JOB_DETAILS_KEYS = ('Country', 'Skills')

    template = "*Title*: {title}\n" \
               "*Date*: {date}\n" \
               "*URL*: [job url]({url})\n" \
               "*Job details*: `{details}`\n" \
               "*Summary*: `{description}`\n\n"

    def __init__(self, channel=None):
        self.bot = TeleBot(TELEGRAM_TOKEN)
        self.channel = TELEGRAM_CHANNEL if channel is None else channel

    def process_item(self, item):
        if item:
            description = item['description'][:self.SUMMARY_LEN] + '...'
            details = ''
            if item['details']:
                for k, v in item['details'].items():
                    if k in self.JOB_DETAILS_KEYS:
                        _details = '{}: {}'.format(k, v)
                        if len(_details) > self.DETAILS_LEN:
                            _details = _details[:self.DETAILS_LEN] + '...'
                        details += _details + '\n'

            message = self.template.format(title=item['title'],
                                           description=description,
                                           url=item['url'],
                                           date=item['published_date'],
                                           details=details.strip() or 'no job details')
            try:
                self.bot.send_message(
                    self.channel, message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                sleep(0.5)
            except Exception as e:
                logger.error(e)

