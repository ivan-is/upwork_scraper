from time import sleep
from pprint import PrettyPrinter
from telebot import TeleBot

from settings import TELEGRAM_TOKEN
from settings import TELEGRAM_CHANNEL
from core.logger import pipe_logger as logger


class PPrintPipeline:

    def __init__(self):
        self.pp = PrettyPrinter(indent=4)

    def process_item(self, item):
        if item:
            self.pp.pprint(item)


class TelegramPipeline:

    SUMMARY_LEN = 120
    JOB_DETAILS_KEYS = ('Country', 'Skills')

    template = "*Title*: {title}\n" \
               "*Date*: {date}\n" \
               "*URL*: [job url]({url})\n" \
               "{details}" \
               "*Summary*: `{description}`\n\n"

    def __init__(self, channel=None):
        self.bot = TeleBot(TELEGRAM_TOKEN)
        self.channel = TELEGRAM_CHANNEL if channel is None else channel

    def _send_msg(self, msg, page_preview=True):
        self.bot.send_message(
            self.channel, msg,
            parse_mode='Markdown',
            disable_web_page_preview=page_preview
        )

    def process_item(self, item):
        if item:
            description = item['description'][:self.SUMMARY_LEN] + '...'
            details = ''
            if item.get('details'):
                skills = item['details'].get('Skills')
                country = item['details'].get('Country')
                if skills:
                    details += '*Skills*: {}\n'.format(skills)
                if country:
                    details += '*Country*: {}\n'.format(country)

            message = self.template.format(title=item['title'],
                                           description=description,
                                           url=item['url'],
                                           date=item['published_date'],
                                           details=details)
            try:
                self._send_msg(message)
                sleep(1)
            except Exception as e:
                msg = '{}: {}'.format(e, item)
                logger.error(msg)
                msg = '\n\n*Malformed message*: `{}`\n\n'.format(message)
                self._send_msg(msg)
