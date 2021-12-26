import threading
import time
from .user_info_crawler import UserInfoCrawler
from .user_relation_crawler import UserRelationCrawler
from .message_crawler import MessageCrawler, UrlCrawler, TopicCrawler, MessageRelationCrawler, UserMsgIndexCrawler

class CrawlerFactory:
    def __init__(self, pools) -> None:
        self.pools = pools

    def startCrawlerThreads(self, num):
        threads = self._makeCrawlerThreads(num)
        for thread in threads:
            thread.start()

    def _makeCrawlerThreads(self, num):
        threadsList = []

        for i in range(num):
            threadsList.append(
                threading.Thread(target = self._startCrawler)
            )
        
        return threadsList
    
    def _isUidDuplicated(self, uid):
        # TODO: Check if uid is duplicated in database
        pass

    def _startCrawler(self):
        # Prepare for crawler
        userInfoCrawler = UserInfoCrawler(self.pools['user'])
        msgInfoCrawler = MessageCrawler(self.pools['msg'])
        urlCrawler = UrlCrawler(self.pools['url'])
        topicCrawler = TopicCrawler(self.pools['topic'])
        msgRelationCrawler = MessageRelationCrawler(self.pools['msgRelation'])
        userMsgIndexCrawler = UserMsgIndexCrawler(self.pools['userMsg'])
        userRelationCrawler = UserRelationCrawler(self.pools['userRelation'])

        while True:
            currentUid = self.pools['uid'].get()
            
            if currentUid:
                print('------ Start crawl user: %s ------' % (str(currentUid)))
                # Get user info
                isValid = userInfoCrawler.getContent(uid=currentUid)

                # Check validity
                if not isValid:
                    print('------ Invalid crawl: %s ------' % (str(currentUid)))
                    time.sleep(1)
                    continue

                time.sleep(1)

                # Get message and other related info
                msgInfoCrawler.getContent(
                    uid=currentUid,
                    urlCrawler=urlCrawler,
                    topicCrawler=topicCrawler,
                    msgRelationCrawler=msgRelationCrawler,
                    userMsgIndexCrawler=userMsgIndexCrawler
                )
                time.sleep(1)

                # Get user relation ship info
                userRelationCrawler.getContent(
                    uid=currentUid,
                    uidPool=self.pools['uid']
                )
                print('------ End crawl user: %s ------' % (str(currentUid)))








