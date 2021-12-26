import pandas as pd
import re
import numpy as np
import sys
sys.path.append("..")
from content_classify.lda_svm import LdaSvmPredict
from preprocess.msg_preprocess import MsgPrepocessor
from base_metrics import BaseMetrics

class InfoMetricsCalculator(BaseMetrics):        
    def _assignContentClass(self):
        '''
        Assign class label for each msg
        '''

        # First preprocess the message
        msgPrepocessor = MsgPrepocessor('', '')
        self.msgInfoDF['text_content'] = self.msgInfoDF['text_content'].apply(msgPrepocessor._applyFunc)
        print('------ msg preprocess done ------')

        # Load LDA-SVM predictor
        predictor = LdaSvmPredict(
            bestTopicNum=130,
            modelPath='../content_classify/model/best_model_topic_130_fold_1',
            ldaPath='../content_classify/model/lda_130.model',
            dictionaryPath='../content_classify/model/word_dictionary.dict',
            labelPath='../content_classify/model/label',
        )

        self.msgInfoDF['text_type'] = self.msgInfoDF['text_content'].apply(lambda x: predictor.singlePredict(x)[0])
        print('------ msg classification done ------')
    
    def _typeRatio(self):
        '''
        Calculate each type ratio in all message
        '''
        typeCountFromOrigin = dict(self.msgInfoDF[self.msgInfoDF['type'] == 0]['text_type'].value_counts(normalize=True))
        typeCountFromRepost = dict(self.msgInfoDF[self.msgInfoDF['type'] == 1]['text_type'].value_counts(normalize=True))
        
        # The ratio of I(c) in I(t)
        self.msgInfoDF['type_ratio_total_origin'] = self.msgInfoDF['text_type'].apply(lambda x: typeCountFromOrigin[x] if x in typeCountFromOrigin else 0)

        # The ratio of I(c) in I(r)
        self.msgInfoDF['type_ratio_total_repost'] = self.msgInfoDF['text_type'].apply(lambda x: typeCountFromRepost[x] if x in typeCountFromRepost else 0)

        print('------ total type ratio done ------')

    def _urlFrequency(self):
        '''
        Calculate url frequency in text_content
        '''
        # Make url frequency dict
        urlFreqDict = {}
        
        def addToUrlFreqDict(word):
            # Extract url
            url = re.search(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', str(word))
            if url:
                urlFreqDict[url[0]] = urlFreqDict.get(url[0], 0) + 1
                return url[0]
            else:
                return ''
        
        def getUrlFreq(word):
            url = re.search(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', str(word))
            if url:
                return urlFreqDict[url[0]]
            else:
                return 0

        self.msgInfoDF['url'] = self.msgInfoDF['text_content'].apply(lambda x: addToUrlFreqDict(x))
        totalTimes = sum(urlFreqDict.values())
        for key in urlFreqDict:
            urlFreqDict[key] = urlFreqDict[key] / totalTimes

        self.msgInfoDF['url_frequency'] = self.msgInfoDF['text_content'].apply(lambda x: getUrlFreq(x))
        print('------ url frequency done ------')
    
    def _topicFrequency(self):
        '''
        Calculate topic frequency in text_content
        '''
        # Make url frequency dict
        topicFreqDict = {}
        
        def addToTopicFreqDict(word):
            # Extract topic
            topics = re.findall(r'#(.*?)#', str(word))
            if topics:
                for topic in topics:
                    topicFreqDict[topic] = topicFreqDict.get(topic, 0) + 1

                return '||'.join(topics)
            else:
                return ''
        
        def getTopicFreq(word):
            topics = re.findall(r'#(.*?)#', str(word))
            if topics:
                res = 0
                for topic in topics:
                    res += topicFreqDict[topic]
                return res
            else:
                return 0

        self.msgInfoDF['topic'] = self.msgInfoDF['text_content'].apply(lambda x: addToTopicFreqDict(x))
        totalTimes = sum(topicFreqDict.values())
        for key in topicFreqDict:
            topicFreqDict[key] = topicFreqDict[key] / totalTimes

        self.msgInfoDF['topic_frequency'] = self.msgInfoDF['text_content'].apply(lambda x: getTopicFreq(x))
        print('------ topic frequency done ------')

    def _isAtOthers(self):
        '''
        Find if @xxx in content
        '''
        def isSatisfyAtOthers(word):
            word = str(word).split('//')[0]
            return 1 if '@' in word else 0
        
        self.msgInfoDF['at_others'] = self.msgInfoDF['text_content'].apply(lambda x: isSatisfyAtOthers(x))
        print('------ @ others done ------')
    
    def infoFeature(self):
        '''
        Calculate the info feature
        '''
        print('====== Start Calculate Info Feature ======')
        self._urlFrequency()
        self._topicFrequency()
        self._isAtOthers()
        self._assignContentClass()
        self._typeRatio()
        print('====== End Calculate Info Feature ======')
    
    
