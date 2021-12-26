from .base_crawler import BaseCrawler
import time
import sys
from .config import BLOG_MAX_PAGE, FAILED_MAX_TIMES
sys.path.append("..")
from util import convertTimeToStamp

class MessageCrawler(BaseCrawler):
    def getContent(self, **kwargs):
        '''
        Get user blog content
        '''

        maxPage = BLOG_MAX_PAGE
        currentPage = 1
        uid = kwargs['uid']
        urlCrawler = kwargs['urlCrawler']
        topicCrawler = kwargs['topicCrawler']
        msgRelationCrawler = kwargs['msgRelationCrawler']
        userMsgIndexCrawler = kwargs['userMsgIndexCrawler']

        while currentPage <= maxPage:
            msgUrl = 'https://weibo.com/ajax/statuses/mymblog?uid={}&page={}&feature=0'.format(uid, currentPage)
            messageInfo = self._getResponse(msgUrl, html=False)
            failedCountTimes = 0

            try:
                for singleMsg in messageInfo['data']['list']:
                    finalInfo = self._wrapContent(uid, singleMsg)
                    
                    self._sendToDataPool(finalInfo)

                    # Pass other unparsed information to other crawlers
                    # Pass to Url crawler
                    if 'url_struct' in singleMsg.keys():
                        urlCrawler.getContent(content=singleMsg['url_struct'])
                    
                    # Pass to topic crawler
                    if 'topic_struct' in singleMsg.keys():
                        topicCrawler.getContent(content=singleMsg['topic_struct'])

                    # Pass to message relation crawler
                    trans = None
                    if 'retweeted_status' in singleMsg.keys():
                        trans = singleMsg['retweeted_status']
                        msgRelationCrawler.getContent(cur=finalInfo, trans=trans)
                    
                    # Pass to user message indexing crawler
                    userMsgIndexCrawler.getContent(cur=finalInfo, trans=trans)
                    
                    
                currentPage += 1
                time.sleep(1)
            except Exception as e:
                failedCountTimes += 1

                # if failedCountTimes >= FAILED_MAX_TIMES:
                #     return 

                currentPage += 1
                continue
            
    def _wrapContent(self, uid, info):
        msgInfo = {
            'msg_id': str(info['id']),
            'uid': uid,
            'text_content': info['text_raw'],
            'url_content': 1 if 'url_struct' in info.keys() and len(info['url_struct']) > 0 else 0,
            'topic_content': 1 if 'topic_struct' in info.keys() and len(info['topic_struct']) > 0 else 0,
            'type': 1 if 'retweeted_status' in info.keys() else 0,
            'comment_count': info['comments_count'],
            'trans_count': info['reposts_count'],
            'favori_count': info['attitudes_count'],
            'msg_time': convertTimeToStamp(info['created_at']),
        }

        return msgInfo

class UrlCrawler(BaseCrawler):
    def getContent(self, **kwargs):
        '''
        Parse url information
        '''
        urlContent = kwargs['content']

        for urlInfo in urlContent:
            try:
                finalInfo = self._wrapContent(urlInfo)
                self._sendToDataPool(finalInfo)
            except:
                continue

    def _wrapContent(self, urlInfo):
        return {
            'url_id': urlInfo['page_id'],
            'url_content': urlInfo['url_title'],
            'url_domain': urlInfo['long_url'],
        }

class TopicCrawler(BaseCrawler):
    def getContent(self, **kwargs):
        '''
        Parse topic information
        '''

        topicContent = kwargs['content']

        for topicInfo in topicContent:
            try:
                finalInfo = self._wrapContent(topicInfo)
                self._sendToDataPool(finalInfo)
            except:
                continue
        
    def _wrapContent(self, topicInfo):
        return {
            'topic_content': topicInfo['topic_title'],
        }

class MessageRelationCrawler(BaseCrawler):
    def getContent(self, **kwargs):
        '''
        Parse relation information
        '''

        curInfo = kwargs['cur']
        transInfo = kwargs['trans']

        try:
            finalInfo = self._wrapContent(curInfo, transInfo)
            self._sendToDataPool(finalInfo)
        except Exception as e:
            return
    
    def _wrapContent(self, curInfo, transInfo):
        return {
            'cur_user_id': curInfo['uid'],
            'cur_msg_id': curInfo['msg_id'],
            'tran_msg_id': transInfo['idstr'],
            'tran_user_id': transInfo['user']['idstr'],
            'time_t': curInfo['msg_time']
        }

class UserMsgIndexCrawler(BaseCrawler):
    def getContent(self, **kwargs):
        '''
        Parse user message indexing info
        '''
        curInfo = kwargs['cur']
        transInfo = kwargs['trans']

        try:
            finalInfo = self._wrapContent(curInfo, transInfo)
            self._sendToDataPool(finalInfo)
        except Exception as e:
            return
    
    def _wrapContent(self, curInfo, transInfo):
        return {
            'uid': curInfo['uid'],
            'author_id': transInfo['user']['idstr'] if transInfo else curInfo['uid'],
            'msg_id': curInfo['msg_id'],
            'time_t': curInfo['msg_time'],
        }













    







