from core.pipelines import TelegramPipeline
from core.logger import setup_logger

setup_logger(log_file=None,
             stdout=True,
             level='DEBUG')

FEED = {
    'title': 'Need an experienced growth hacker - Upwork',
    'url': 'https://www.upwork.com/jobs/Need-experienced-growth-hacker_%7E0191d670e0423653b9',
    'description': 'We are a digital strategy company and we help companies and startups to grow. We...',
    'published_date': 'Mon, 09 Oct 2017 09:31:19 +0000',
    'details': {'Category': 'Sales &amp; Marketing &gt; Other - Sales &amp; Mar...',
                'Posted On': 'October 09, 2017 09:47 UTC...',
                'Skills': 'Lead Generation, Microsoft Excel, PHP, Social Medi...',
                'Country': 'Switzerland...'},
    'id': 1909116731639418407
}


if __name__ == '__main__':
    pipe = TelegramPipeline(channel='@glancepro_test')
    pipe.process_item(FEED)
