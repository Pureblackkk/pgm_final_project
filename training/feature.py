import sys
import math
from networkx.classes.function import neighbors
import numpy as np

from numpy.lib.utils import info
sys.path.append('..')
from dynamic_metrics_calculator.metrics import MetricsCalculator


class BaseFeature:
    def __init__(self) -> None:
        self.metricsCal = MetricsCalculator('../../data/database_after_static/')


class InfoFeature(BaseFeature):
    def _getCheckedMetrics(self, metrics):
        if len(metrics) == 0:
            return 0
        else:
            return metrics[0]
    
    def _getInfoMetrics(self, metricsName, messageId):
        return self.metricsCal.msgInfoDF[self.metricsCal.msgInfoDF['msg_id'].astype(str) == messageId][metricsName].values

    def _getAuthorMetrics(self, metricsName, uid):
        return self.metricsCal.userInfoDF[self.metricsCal.userInfoDF['uid'].astype(str) == uid][metricsName].values

    def messageTypeInTotalOrigin(self, messageId, Y):
        metrics = self._getInfoMetrics('type_ratio_total_origin', messageId)
        metrics = self._getCheckedMetrics(metrics)
        return Y * metrics
            
    def messageTypeInTotalRepost(self, messageId, Y):
        metrics = self._getInfoMetrics('type_ratio_total_repost', messageId)
        metrics = self._getCheckedMetrics(metrics)
        return Y * metrics
    
    def isUrlContained(self, messageId, Y):
        metrics = self._getInfoMetrics('url_content', messageId)
        metrics = self._getCheckedMetrics(metrics)
        return Y * metrics
    
    def urlFrequency(self, messageId, Y):
        metrics = self._getInfoMetrics('url_frequency', messageId)
        metrics = self._getCheckedMetrics(metrics)
        return Y * metrics
    
    def isTopicContained(self, messageId, Y):
        metrics = self._getInfoMetrics('topic_content', messageId)
        metrics = self._getCheckedMetrics(metrics)
        return Y * metrics
    
    def topicFrequency(self, messageId, Y):
        metrics = self._getInfoMetrics('topic_frequency', messageId)
        metrics = self._getCheckedMetrics(metrics)
        return Y * metrics
    
    def isAtOthers(self, messageId, Y):
        metrics = self._getInfoMetrics('at_others', messageId)
        metrics = self._getCheckedMetrics(metrics)
        return Y * metrics
    
    def fansByFollowNum(self, authorId, Y):
        fanNum = self._getCheckedMetrics(self._getAuthorMetrics('fans_count', authorId))
        followNum = self._getCheckedMetrics(self._getAuthorMetrics('follow_count', authorId))
        return Y * math.log(fanNum / followNum)
    
    def isVerified(self, authorId, Y):
        metrics = self._getCheckedMetrics(self._getAuthorMetrics('certify_v', authorId))
        metrics = self._getCheckedMetrics(metrics)
        return Y * metrics
    
    def getInfoFeatureVector(self, uid, messageId, Y):
        infoVec = []
        infoVec.append(self.messageTypeInTotalOrigin(messageId, Y))
        infoVec.append(self.messageTypeInTotalRepost(messageId, Y))
        infoVec.append(self.isUrlContained(messageId, Y))
        infoVec.append(self.urlFrequency(messageId, Y))
        infoVec.append(self.isTopicContained(messageId, Y))
        infoVec.append(self.topicFrequency(messageId, Y))
        infoVec.append(self.isAtOthers(messageId, Y))
        infoVec.append(self.fansByFollowNum(uid, Y))
        infoVec.append(self.isVerified(uid, Y))

        infoVec = np.array(infoVec)
        return infoVec

class UserFeature(BaseFeature):
    def contentTypeUserRatio(self, uid, textType, ratioType, Y):
        metrics = self.metricsCal.getTypeRatio(uid, textType, ratioType)
        return Y * metrics
    
    def urlUserRepostRatio(self, uid, url, Y):
        metrics = self.metricsCal.getUrlRatioInUserRepost(uid, url)
        return Y * metrics
    
    def topicUserRepostRatio(self, uid, topic, Y):
        metrics = self.metricsCal.getTopicRatioInUserRepost(uid, topic)
        return Y * metrics
    
    def userAuthorRelationSimilarity(self, uid, authorId, similarObjcet, Y):
        metrics = self.metricsCal.getRelationSimilarity(uid, authorId, similarObjcet)
        return Y * metrics
    
    def commonRepostRatio(self, uid, authorId, Y):
        metrics = self.metricsCal.getCommonRepost(uid, authorId)
        return Y * metrics
    
    def textSimilarity(self, uid, text, Y):
        metrics = self.metricsCal.getTextSimilarity(uid, text) 
        return Y * metrics
    
    def tagSimilarity(self, uid, authorId, Y):
        metrics = self.metricsCal.getTagSimilar(uid, authorId)
        return Y * metrics
    
    def descriptionSimilarity(self, uid, authorId, Y):
        metrics = self.metricsCal.getDescriptionSimilar(uid, authorId)
        return Y * metrics
    
    def getUserFeatureVector(self, uid, authorId, messageParam, Y):
        textType = messageParam['textType']
        url = messageParam['url']
        topic = messageParam['topic']
        text = messageParam['text']

        userVec = []
        userVec.append(self.contentTypeUserRatio(uid, textType, 'own-origin', Y))
        userVec.append(self.contentTypeUserRatio(uid, textType, 'own-repost', Y))
        userVec.append(self.contentTypeUserRatio(uid, textType, 'fan-origin', Y))
        userVec.append(self.contentTypeUserRatio(uid, textType, 'fan-repost', Y))
        userVec.append(self.contentTypeUserRatio(uid, textType, 'follow-origin', Y))
        userVec.append(self.contentTypeUserRatio(uid, textType, 'follow-repost', Y))

        userVec.append(self.urlUserRepostRatio(uid, url, Y))
        userVec.append(self.topicUserRepostRatio(uid, topic, Y))

        userVec.append(self.userAuthorRelationSimilarity(uid, authorId, 'fan', Y))
        userVec.append(self.userAuthorRelationSimilarity(uid, authorId, 'follow', Y))

        userVec.append(self.commonRepostRatio(uid, authorId, Y))
        userVec.append(self.textSimilarity(uid, text, Y))
        userVec.append(self.tagSimilarity(uid, authorId, Y))
        userVec.append(self.descriptionSimilarity(uid, authorId, Y))

        userVec = np.array(userVec)
        return userVec

class RelationFeature(BaseFeature):
    def userRelation(self, uidv, uidw, Yv, Yw):
        metrics = self.metricsCal.getUserRelation(uidv, uidw)
        if not metrics:
            return None

        if metrics == 'type3':
            if Yv and Yw:
                return 1
            elif Yv or Yw:
                return 0.5
            return 0
        
        if metrics == 'type1':
            if Yw and Yv:
                return 1
            elif Yw and not Yv:
                return 0.5
            return 0
        
        if metrics == 'type2':
            if Yw and Yv:
                return 1
            elif Yv and not Yw:
                return 0.5
            return 0
        
    def textsimilarBetweenNeighbor(self, uidv, uidw, Yv, Yw):
        metrics = self.metricsCal.getTextsimilarBetween(uidv, uidw)

        if not metrics:
            return 0

        return Yv * Yw * metrics
    
    def commonPostBetweenNeighbor(self, uidv, uidw, authorId, Yv, Yw):
        metrics = self.metricsCal.getCommonPostNumber(uidv, uidw, authorId)
        return Yv * Yw * metrics

    def getRelationFeatureVector(self, uidv, uidw, authorId, Yv, Yw):
        relationVec = []

        relationVec.append(self.userRelation(uidv, uidw, Yv, Yw))
        relationVec.append(self.textsimilarBetweenNeighbor(uidv, uidw, Yv, Yw))
        relationVec.append(self.commonPostBetweenNeighbor(uidv, uidw, authorId, Yv, Yw))

class FeatureCalculator(InfoFeature, UserFeature, RelationFeature):
    pass

        




    

    