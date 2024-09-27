from scrapy import signals
import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        user_agent = random.choice(spider.settings.get('USER_AGENT_LIST'))
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)