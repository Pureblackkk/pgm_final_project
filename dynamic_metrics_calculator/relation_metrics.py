from .base_metrics import BaseMetrics
import numpy as np

class RelationMetricsCalculator(BaseMetrics):
    def getUserRelation(self, uidv, uidw):
        '''
        Get userV and userW relation ship
        @return:
            type1: v is w's fan
            type2: w is v's fan
            type3: v and w are both each others' fan
        '''
        
        v2w = self.userRelationDF[(self.userRelationDF['uid'].astype(str) == uidv) & (self.userRelationDF['follow_id'].astype(str) == uidw)]['type'].values

        if len(v2w) == 0:
            return None
        elif len(v2w) == 1:
            return 'type1' if int(v2w[0]) == 1 else 'type2'
        elif len(v2w) == 2:
            return 'type3'

    def getTextsimilarBetween(self, uidv, uidw):
        def getAvgVec(uid):
            avgVec = self.userInfoDF[self.userInfoDF['uid'].astype(str) == uid]['avg_word_vector'].values
            if len(avgVec):
                avgVec = avgVec[0].split('||')
                avgVec = [float(x) for x in avgVec]
                return avgVec
            else:
                return None

        uidvAvg = getAvgVec(uidv)
        uidwAvg = getAvgVec(uidw)
        if uidvAvg and uidwAvg:
            return np.dot(uidvAvg, uidwAvg) / (np.sqrt(np.dot(uidvAvg, uidvAvg)) * np.sqrt(np.dot(uidwAvg, uidwAvg)))
        else:
            return None

    def getCommonPostNumber(self, uidv, uidw, authorId):
        uservRepostSet = set(self.msgRelationDF[self.msgRelationDF['cur_user_id'].astype(uidv) == uidv]['tran_msg_id'].tolist())

        userwRepostSet = set(self.msgRelationDF[self.msgRelationDF['cur_user_id'].astype(uidv) == uidw]['tran_msg_id'].tolist())

        authorRepostSet = set(self.msgRelationDF[self.msgRelationDF['cur_user_id'].astype(uidw) == authorId]['tran_msg_id'].tolist())

        commonRepost = uservRepostSet & userwRepostSet & authorRepostSet

        return len(commonRepost) / (len(uservRepostSet) * len(userwRepostSet) * len(authorRepostSet))**(1/3)

