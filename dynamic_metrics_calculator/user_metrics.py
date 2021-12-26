from .base_metrics import BaseMetrics
import numpy as np
import json
import math
import sys
sys.path.append('..')
from text_similarity.word2vec import MyWord2Vec

USER_TEXT_TYPE_RATIO_MAP = {
    'own-origin': 'content_type_own_origin_dict',
    'own-repost': 'content_type_own_repost_dict',
    'fan-origin': 'content_type_fan_origin_dict',
    'fan-repost': 'content_type_fan_repost_dict',
    'follow-origin': 'content_type_follow_origin_dict',
    'follow-repost': 'content_type_follow_repost_dict',
}

class UserMetricsCalculator(BaseMetrics):
    def __init__(self, databaseDirectory) -> None:
        super().__init__(databaseDirectory)
        self.word2Vec = MyWord2Vec('../text_similarity/model/blog_150000.model')

    def getTypeRatio(self, uid, textType, ratioType):
        '''
        Get different kind of type ratio
        '''

        contentTypeDict = self.userInfoDF[(self.userInfoDF['uid'].astype(str) == uid)]
        if len(contentTypeDict):
            contentTypeDict = json.loads(contentTypeDict[USER_TEXT_TYPE_RATIO_MAP[ratioType]].values[0])
            if textType in contentTypeDict.keys():
                return contentTypeDict[textType]
            else:
                return 0.0
        else:
            return 0.0
    
    def getUrlRatioInUserRepost(self, uid, url):
        '''
        Get the url frequency in user repost
        '''

        userTextList = self.msgInfoDF[self.msgInfoDF['uid'].astype(str) == uid]['text_content'].tolist()
        
        if len(userTextList) == 0:
            return 0.0
        
        count = 0

        for content in userTextList:
            if url in content:
                count += 1

        return count / len(userTextList)

    def getTopicRatioInUserRepost(self, uid, topic):
        '''
        Get topic frequency in user repost
        '''
        topics = self.msgInfoDF[self.msgInfoDF['uid'].astype(str) == uid]['topic'].dropna().tolist()
        topics= '||'.join(topics)
        topicsList = topics.split('||')

        if len(topicsList) == 0:
            return 0.0
        
        count = 0

        for content in topicsList:
            if topic == content:
                count += 1
        return count / len(topicsList)

    def getRelationSimilarity(self, uid1, uid2, similarObject):
        if similarObject == 'fan':
            uid1FansSet1 = set(self.userRelationDF[(self.userRelationDF['uid'] == uid1) & (self.userRelationDF['type'] == 0)]['follow_id'].tolist())
            uid1FansSet2 = set(self.userRelationDF[(self.userRelationDF['follow_id'] == uid1) & (self.userRelationDF['type'] == 1)]['uid'].tolist())
            uid1FansSet = uid1FansSet1|uid1FansSet2

            uid2FansSet1 = set(self.userRelationDF[(self.userRelationDF['uid'] == uid2) & (self.userRelationDF['type'] == 0)]['follow_id'].tolist())
            uid2FansSet2 = set(self.userRelationDF[(self.userRelationDF['follow_id'] == uid2) & (self.userRelationDF['type'] == 1)]['uid'].tolist())
            uid2FanSet = uid2FansSet1|uid2FansSet2

            commonFansSet = uid1FansSet & uid2FanSet
            return len(commonFansSet) / math.sqrt((len(uid1FansSet) * len(uid2FanSet)))
        elif similarObject == 'follow':
            uid1FollowSet1 = set(self.userRelationDF[(self.userRelationDF['uid'] == uid1) & (self.userRelationDF['type'] == 1)]['follow_id'].tolist())
            uid1FollowSet2 = set(self.userRelationDF[(self.userRelationDF['follow_id'] == uid1) & (self.userRelationDF['type'] == 0)]['uid'].tolist())
            uid1FollowSet = uid1FollowSet1|uid1FollowSet2

            uid2FollowSet1 = set(self.userRelationDF[(self.userRelationDF['uid'] == uid2) & (self.userRelationDF['type'] == 1)]['follow_id'].tolist())
            uid2FollowSet2 = set(self.userRelationDF[(self.userRelationDF['follow_id'] == uid2) & (self.userRelationDF['type'] == 0)]['uid'].tolist())
            uid2FollowSet = uid2FollowSet1|uid2FollowSet2

            commonFollowSet = uid1FollowSet&uid2FollowSet
            return len(commonFollowSet) / math.sqrt((len(uid1FollowSet) * len(uid2FollowSet)))

    def getCommonRepost(self, uid, authorId):
        userRepostSet = set(self.msgRelationDF[self.msgRelationDF['cur_user_id'].astype(uid) == uid]['tran_msg_id'].tolist())

        authorRepostSet = set(self.msgRelationDF[self.msgRelationDF['cur_user_id'].astype(uid) == authorId]['tran_msg_id'].tolist())

        commonRepost = userRepostSet & authorRepostSet

        return len(commonRepost) / math.sqrt(len(userRepostSet) * len(authorRepostSet))

    def getTextSimilarity(self, uid, text):
        textVec = self.word2Vec.convertWord(text)
        avgVec = self.userInfoDF[self.userInfoDF['uid'].astype(str) == uid]['avg_word_vector'].values[0].split('||')
        avgVec = [float(x) for x in avgVec]

        # Calculate distance 
        return np.dot(textVec, avgVec) / (np.sqrt(np.dot(textVec, textVec)) * np.sqrt(np.dot(avgVec, avgVec)))

    def getTagSimilar(self, uid, authorId):
        def getTag(uid):
            return self.userInfoDF[self.userInfoDF['uid'].astype(str) == uid]['tags'].values[0]
        userTag = getTag(uid)
        authorTag = getTag(authorId)

        return self.word2Vec.getTextSimilarity((userTag, authorTag))
    
    def getDescriptionSimilar(self, uid, authorId):
        def getDescription(uid):
            return self.userInfoDF[self.userInfoDF['uid'].astype(str) == uid]['user_description'].values[0]
        userDescription = getDescription(uid)
        authorDescription = getDescription(authorId)

        return self.word2Vec.getTextSimilarity((userDescription, authorDescription))

