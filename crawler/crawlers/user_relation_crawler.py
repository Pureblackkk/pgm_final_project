from .base_crawler import BaseCrawler
from .config import FOLLOWER_MAX_NUM, FOLLOWER_MAX_PAGE
import time

class UserRelationCrawler(BaseCrawler):
    def getContent(self, **kwargs):
        '''
        Get user's follows
        '''

        uid = kwargs['uid']
        uidPool = kwargs['uidPool']
        currentPage = 1
        currentHeadCount = 0
        selectedHeadCount = 0
        maxHeadCount = FOLLOWER_MAX_NUM

        # Get total follower number
        followUrl = 'https://weibo.com/ajax/friendships/friends?page={}&uid={}'.format(currentPage, uid)
        followInfo = self._getResponse(followUrl, html=False)

        if followInfo:
            followTotalNum = followInfo['total_number']
            time.sleep(1)

            # Get Follower
            while selectedHeadCount < maxHeadCount and currentHeadCount < followTotalNum and currentPage < FOLLOWER_MAX_PAGE:
                followUrl = 'https://weibo.com/ajax/friendships/friends?page={}&uid={}'.format(currentPage, uid)
                followInfo = self._getResponse(followUrl, html=False)

                try:
                    for follower in followInfo['users']:
                        # First check if validity
                        validity = self._checkValidity(follower)

                        if not validity:
                            currentHeadCount += 1
                            continue

                        finalInfo = self._wrapContent(uid, follower, 1)

                        # Send new uid into uid pool
                        uidPool.put(finalInfo['follow_id'])

                        # Send realtion data to relation pool
                        self._sendToDataPool(finalInfo)

                        # Add head count
                        currentHeadCount += 1
                        selectedHeadCount += 1
                    
                    currentPage += 1
                    time.sleep(1)
                except:
                    currentHeadCount += 20
                    currentPage += 1
        
        # Get fans total 
        currentPage = 1
        currentHeadCount = 0
        selectedHeadCount = 0

        fansUrl = 'https://weibo.com/ajax/friendships/friends?relate=fans&page={}&uid={}&type=all&newFollowerCount=0'.format(currentPage, uid)
        fansInfo = self._getResponse(fansUrl, html=False)

        if fansInfo:
            fanTotalNum = fansInfo['total_number']
            time.sleep(1)
            
            # Get Fans
            while selectedHeadCount < maxHeadCount and currentHeadCount < fanTotalNum and currentPage < FOLLOWER_MAX_PAGE:
                fansUrl = 'https://weibo.com/ajax/friendships/friends?relate=fans&page={}&uid={}&type=all&newFollowerCount=0'.format(currentPage, uid)
                fansInfo = self._getResponse(fansUrl, html=False)

                try:
                    for fan in fansInfo['users']:
                        # First check if validity
                        validity = self._checkValidity(fan)

                        if not validity:
                            currentHeadCount += 1
                            continue

                        finalInfo = self._wrapContent(uid, fan, 0)

                        # Send new uid into uid pool
                        uidPool.put(finalInfo['follow_id'])

                        # Send realtion data to relation pool
                        self._sendToDataPool(finalInfo)

                        # Add head count
                        currentHeadCount += 1
                        selectedHeadCount += 1

                    currentPage += 1
                    time.sleep(1)
                except:
                    currentHeadCount += 20
                    currentPage += 1

    def _wrapContent(self, uid, follower, type):
        return {
            'uid': uid,
            'follow_id': follower['idstr'],
            'type': type,
        }
    
    def _checkValidity(self, follower):
        if follower['followers_count'] < 100:
            return False
        else:
            return True




        