from locale import NOEXPR
from base_metrics import BaseMetrics
import json
import numpy as np
import sys
sys.path.append('..')
from text_similarity.word2vec import MyWord2Vec

class UserMetricsCalculator(BaseMetrics):
    def __init__(self, databaseDirectory) -> None:
        super().__init__(databaseDirectory)
        self.word2Vec = MyWord2Vec('../text_similarity/model/blog_150000.model')

    def _repostRatio(self):
        def getRepostRatio(x):
            currentUserType = self.msgInfoDF[self.msgInfoDF['uid'] == x]['type']
            try:
                return currentUserType.value_counts(normalize=True)[1]
            except:
                return 0.0
            
        self.userInfoDF['repost_ratio'] = self.userInfoDF['uid'].apply(lambda x: getRepostRatio(x))
        print('------ repost ratio done ------')

    def _contentTypeOwnRatio(self):
        def getContentTypeRatio(uid, isRepost):
            ratioDict = self.msgInfoDF[(self.msgInfoDF['uid'] == uid) & (self.msgInfoDF['type'] == isRepost)]['text_type'].value_counts(normalize=True)
            if len(ratioDict):
                return json.dumps(dict(ratioDict))
            else: 
                return None

        self.userInfoDF['content_type_own_origin_dict'] = self.userInfoDF['uid'].apply(lambda x: getContentTypeRatio(x, 0))
        self.userInfoDF['content_type_own_repost_dict'] = self.userInfoDF['uid'].apply(lambda x: getContentTypeRatio(x, 1))
        print('------ own text type ratio dict done ------')

    def _contentTypeFanRatio(self):
        def getFans(uid):
            fansSet1 = set(self.userRelationDF[(self.userRelationDF['uid'] == uid) & (self.userRelationDF['type'] == 0)]['follow_id'].tolist())
            fansSet2 = set(self.userRelationDF[(self.userRelationDF['follow_id'] == uid) & (self.userRelationDF['type'] == 1)]['uid'].tolist())
            fansSet = fansSet1 | fansSet2
            return fansSet
        
        def getContentTypeRatio(uidSet, isRepost):
            ratioDict = self.msgInfoDF[(self.msgInfoDF['uid'].isin(uidSet)) & (self.msgInfoDF['type'] == isRepost)]['text_type'].value_counts(normalize=True)
            if len(ratioDict):
                return json.dumps(dict(ratioDict))
            else: 
                return None

        self.userInfoDF['content_type_fan_origin_dict'] = self.userInfoDF['uid'].apply(lambda x: getContentTypeRatio(getFans(x), 0))
        self.userInfoDF['content_type_fan_repost_dict'] = self.userInfoDF['uid'].apply(lambda x: getContentTypeRatio(getFans(x), 1))
        print('------ fan text type ratio dict done ------')

    def _contentTypeFollowRatio(self):
        def getFollows(uid):
            fansSet1 = set(self.userRelationDF[(self.userRelationDF['uid'] == uid) & (self.userRelationDF['type'] == 1)]['follow_id'].tolist())
            fansSet2 = set(self.userRelationDF[(self.userRelationDF['follow_id'] == uid) & (self.userRelationDF['type'] == 0)]['uid'].tolist())
            fansSet = fansSet1 | fansSet2
            return fansSet
        
        def getContentTypeRatio(uidSet, isRepost):
            ratioDict = self.msgInfoDF[(self.msgInfoDF['uid'].isin(uidSet)) & (self.msgInfoDF['type'] == isRepost)]['text_type'].value_counts(normalize=True)
            if len(ratioDict):
                return json.dumps(dict(ratioDict))
            else: 
                return None

        self.userInfoDF['content_type_follow_origin_dict'] = self.userInfoDF['uid'].apply(lambda x: getContentTypeRatio(getFollows(x), 0))
        self.userInfoDF['content_type_follow_repost_dict'] = self.userInfoDF['uid'].apply(lambda x: getContentTypeRatio(getFollows(x), 1))
        print('------ follow text type ratio dict done ------')
    
    def _avgWordVector(self):
        def getAvgWordVector(uid):
            textList = self.msgInfoDF[self.msgInfoDF['uid'] == uid]['text_content'].tolist()
            tempVectList = []
            for text in textList:
                textMeanVector = self.word2Vec.convertWord(text)
                if len(textMeanVector):
                    tempVectList.append(textMeanVector)
            if len(tempVectList):
                res = np.mean(np.array(tempVectList), axis=0)
                res = [str(num) for num in res]
                return '||'.join(res)
            else:
                return ''
            
        self.userInfoDF['avg_word_vector'] = self.userInfoDF['uid'].apply(lambda x: getAvgWordVector(x))
        print('------ avg word vec done ------')

    def userFeature(self):
        '''
        Calculate the user feature
        '''
        print('====== Start Calculate User Feature ======')
        # Calculate text own ratio dict
        self._contentTypeOwnRatio()
        
        # Calculate text fan ratio dict
        self._contentTypeFanRatio()

        # Calculate text follow ratio dict
        self._contentTypeFollowRatio()

        # Calculate avg word vector
        self._avgWordVector()

        # Calculate user repost ratio
        self._repostRatio()
        print('====== End Calculate User Feature ======')
