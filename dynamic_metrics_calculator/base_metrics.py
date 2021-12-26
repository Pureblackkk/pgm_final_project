import pandas as pd

class BaseMetrics:
    def __init__(self, databaseDirectory) -> None:
        self._init(databaseDirectory)
    
    def _init(self, directory):
        self.msgInfoDF = pd.read_csv(directory+'msg_info.csv', encoding='utf-16')
        self.msgRelationDF = pd.read_csv(directory+'msg_relation.csv', encoding='utf-16')
        self.topicInfoDF = pd.read_csv(directory+'topic_info.csv', encoding='utf-16')
        self.urlInfoDF = pd.read_csv(directory+'url_info.csv', encoding='utf-16')
        self.userInfoDF = pd.read_csv(directory+'user_info.csv', encoding='utf-16')
        self.userMsgIndexDF = pd.read_csv(directory+'user_msg_index.csv', encoding='utf-16')
        self.userRelationDF = pd.read_csv(directory+'user_relation.csv', encoding='utf-16')