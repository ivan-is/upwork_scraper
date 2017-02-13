
LOG_LEVEL = 'INFO'
LOG_FILE = 'log/crawler.log'
LOG_TO_STDOUT = False

# graphite
CARBON_SERVER = '172.16.0.3'
CARBON_PORT = 2003

# crawler
REVISIT_AFTER = 180  # sec
URL_FETCH_RETRIES = 5  # max retries for failed requests
CONNECTION_TIMEOUT = 5  # sec
READ_TIMEOUT = 25  # sec

USER_AGENT = 'Mozilla/5.0'
HEADERS = {'User-Agent': USER_AGENT}


# feed urls
URLS = [
    # {
    #     'url': 'https://www.upwork.com/ab/feed/jobs/rss?client_hires=1-9%2C10-&contractor_tier=2%2C3&sort=create_time+desc&api_params=1&securityToken=f780fcdc4c1a7ae785405cd4427284e0ade68423f4a423c366a649347249874860cf266c30df9c3776350f6ebdde870b3e4aa0a4f3d421bf21ee6e1785d886c7&userUid=564684666840989696&orgUid=564684666849378305',
    #     'filter_name': 'base_filter'
    # },
    {
        'url': 'https://www.upwork.com/ab/feed/jobs/rss?budget=250-100000&client_hires=1-9%2C10-&contractor_tier=2%2C3&verified_payment_only=1&q=%28Web+OR+Design+OR+UI+OR+UX+OR+PHP+OR+Laravel+OR+Wordpress+NOT+writer+NOT+translate%29&sort=create_time+desc&api_params=1&securityToken=f780fcdc4c1a7ae785405cd4427284e0ade68423f4a423c366a649347249874860cf266c30df9c3776350f6ebdde870b3e4aa0a4f3d421bf21ee6e1785d886c7&userUid=564684666840989696&orgUid=579929510178926592',
        'filter_name': 'web'
    },
    {
        'url': 'https://www.upwork.com/ab/feed/jobs/rss?budget=250-100000&category2=data_science_analytics&client_hires=1-9%2C10-&contractor_tier=2%2C3&verified_payment_only=1&sort=create_time+desc&api_params=1&q=&securityToken=f780fcdc4c1a7ae785405cd4427284e0ade68423f4a423c366a649347249874860cf266c30df9c3776350f6ebdde870b3e4aa0a4f3d421bf21ee6e1785d886c7&userUid=564684666840989696&orgUid=579929510178926592',
        'filter_name': 'bigdata'
    },
    {
        'url': 'https://www.upwork.com/ab/feed/jobs/rss?budget=250-100000&client_hires=1-9%2C10-&contractor_tier=2%2C3&verified_payment_only=1&q=Devops+OR+Linux+system+administrator+NOT+writer&sort=create_time+desc&api_params=1&securityToken=f780fcdc4c1a7ae785405cd4427284e0ade68423f4a423c366a649347249874860cf266c30df9c3776350f6ebdde870b3e4aa0a4f3d421bf21ee6e1785d886c7&userUid=564684666840989696&orgUid=579929510178926592',
        'filter_name': 'devops'
    },
    {
        'url': 'https://www.upwork.com/ab/feed/jobs/rss?budget=50-100000&client_hires=1-9%2C10-&verified_payment_only=1&q=designer&sort=create_time+desc&api_params=1&securityToken=f780fcdc4c1a7ae785405cd4427284e0ade68423f4a423c366a649347249874860cf266c30df9c3776350f6ebdde870b3e4aa0a4f3d421bf21ee6e1785d886c7&userUid=564684666840989696&orgUid=579929510178926592',
        'filter_name': 'design'
    }
]


try:
    from local_settings import *
except ImportError:
    pass