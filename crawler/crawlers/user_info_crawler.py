from .base_crawler import BaseCrawler
import time 

class UserInfoCrawler(BaseCrawler):
    def getContent(self, **kwargs):
        '''
        Get user info content
        '''

        # Get uid then make request url
        uid = kwargs['uid']
        baseUrl = 'https://weibo.com/ajax/profile/info?custom={}'.format(str(uid))
        time.sleep(1)
        detailUrl = 'https://weibo.com/ajax/profile/detail?uid={}'.format(str(uid))

        baseInfoContent = self._getResponse(baseUrl, html=False)
        deatailInfoContent = self._getResponse(detailUrl, html=False)

        # If not recieve data
        if not baseInfoContent or not deatailInfoContent:
            return False
        
        baseInfoContent = baseInfoContent['data']['user']
        deatailInfoContent = deatailInfoContent['data']
        
        # Wrap info content
        resultInfo = self._wrapContent(uid, baseInfoContent, deatailInfoContent)

        # Check user validity
        valid = self._isUserValid(resultInfo)
        if not valid:
            return False

        # Send the info to pool
        self._sendToDataPool(resultInfo)

        # Return result
        return True

    def _wrapContent(self, uid, base, detail):
        # Make tag
        tag = '||'.join([labels['name'] for labels in detail['label_desc']]) if 'label_desc' in base.keys() else ''
        tag += detail['desc_text']

        # Make whole information
        userInfo = {
            'uid': str(uid),
            'user_name': base['screen_name'],
            'msg_total_count': base['statuses_count'],
            'certify_v': bool(base['verified']),
            'fans_count': base['followers_count'],
            'follow_count': base['friends_count'],
            'user_description': base['description'],
            'city': base['location'],
            'tags': tag
        }

        return userInfo
    
    def _isUserValid(self, resultInfo):
        # If total msg count over 200
        if int(resultInfo['msg_total_count']) < 200:
            return False
        
        # If follow / fans > 10 and post less than 600
        if int(resultInfo['fans_count']) == 0:
            return False

        if int(resultInfo['follow_count']) / int(resultInfo['fans_count']) > 10 and int(resultInfo['msg_total_count']) < 600:
            return False
        
        return True



        




    