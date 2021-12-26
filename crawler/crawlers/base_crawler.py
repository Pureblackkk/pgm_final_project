import time
import requests
import json
import random
import yaml
from abc import ABC, abstractmethod

class BaseCrawler(ABC):
    def __init__(self, pool) -> None:
        self.pool = pool
        self.agents = open('./agent/user_agent.txt').readlines()
        self.cookieList = yaml.load(open('./agent/user_cookie.yaml'), Loader=yaml.FullLoader)
        self.failTimeLimits = 5

    def _randomUserAgent(self):
        '''
        Get request header using agent
        '''

        agentsList = [line.rstrip() for line in self.agents]
        return random.choice(agentsList)
    
    def _randomUserCookie(self):
        '''
        Get request cookie
        '''
        return random.choice(self.cookieList)

    def _getResponse(self, url, html=True, **kwargs):
        '''
        Get user response content by request api
        '''
        
        # Make request header
        if 'headers' not in kwargs:
            kwargs['headers'] = {
                'User-Agent': self._randomUserAgent(),
                'cookie': self._randomUserCookie(),
                "Referer": "https://passport.weibo.com/",
            }
        elif 'User-Agent' not in kwargs['headers']:
            kwargs['headers']['User-Agent'] = self._randomUserAgent()

        # Try to get page data
        failed_times = 0

        while True:
            try:
                proxies = {}
                with requests.get(url, timeout=10, proxies=proxies, **kwargs) as r:
                    r.encoding = 'utf-8'
                    if r.status_code == 412:
                        failed_times += 1
                        kwargs['headers']['User-Agent'] = self._randomUserAgent()
                        kwargs['headers']['cookie'] = self._randomUserCookie()
                        time.sleep(1.5)
                    if r.status_code == 404 or r.status_code >= 500:
                        failed_times += 1
                        time.sleep(1.5)
                        if failed_times > self.failTimeLimits:
                            print('------ Request failed! ------')
                            return None
                    if r.status_code == 414:
                        print('!!!!!! IP Banned. Please change cookies or ip !!!!!!')
                        return None
                    r.raise_for_status()

                    # Parse response in html or json
                    if html:
                        content = r.text
                    else:
                        content = json.loads(r.text)
                    return content
            except Exception as e:
                print(e)
                failed_times += 1
                kwargs['headers']['User-Agent'] = self._randomUserAgent()
                kwargs['headers']['cookie'] = self._randomUserCookie()

                if failed_times > self.failTimeLimits:
                    print('------ Request failed! ------')
                    return None

                time.sleep(1.5)
                continue
    
    def _sendToDataPool(self, data):
        self.pool.put(data)

    @abstractmethod
    def getContent(self):
        '''
        Child must implement get content method
        '''

        pass