from abc import ABC, abstractmethod
import threading
import sys
sys.path.append("..") 
from util import BlogDataBase

class BaseSaver(ABC, threading.Thread):
    def __init__(self, pool) -> None:
        threading.Thread.__init__(self)
        self.savePool = pool
        self.databaseObject = BlogDataBase()
    
    @abstractmethod
    def run(self):
        '''
        Inplement data saving functions
        '''
        pass

class UserInfoSaver(BaseSaver):
    def __init__(self, pool) -> None:
        super().__init__(pool)

    def run(self):
        while True:
            try:
                currentData = self.savePool.get()
                self.databaseObject.writeToTable('user_info', currentData)
                print('Save user info successfully!')
            except Exception as e:
                print('Save user info failed: %s!' % e)

class MsgInfoSaver(BaseSaver):
    def __init__(self, pool) -> None:
        super().__init__(pool)
    
    def run(self):
        while True:
            try:
                currentData = self.savePool.get()
                self.databaseObject.writeToTable('msg_info', currentData)
                print('Save msg info successfully!')
            except Exception as e:
                print('Save msg info failed: %s!' % e)


class UrlInfoSaver(BaseSaver):
    def __init__(self, pool) -> None:
        super().__init__(pool)
    
    def run(self):
        while True:
            currentData = self.savePool.get()
            try:
                # Only insert when it is new url
                if not self.databaseObject.checkIfExists('url_info', 'url_id', currentData['url_id']):
                    self.databaseObject.writeToTable('url_info', currentData)
                    print('Save url info successfully!')
                else:
                    print('Duplicated save url info')
            except Exception as e:
                print('Save url info failed: %s!' % e)


class TopicInfoSaver(BaseSaver):
    def __init__(self, pool) -> None:
        super().__init__(pool)
    
    def run(self):
        while True:
            currentData = self.savePool.get()

            try:
                # Only insert when it is new url
                if not self.databaseObject.checkIfExists('topic_info', 'topic_content', currentData['topic_content']):
                    self.databaseObject.writeToTable('topic_info', currentData)
                    print('Save topic info successfully!')
                else:
                    print('Duplicated save topic info')
            except Exception as e:
                print('Save topic info failed: %s!' % e)

class MsgRelationSaver(BaseSaver):
    def __init__(self, pool) -> None:
        super().__init__(pool)
    
    def run(self):
        while True:
            try:
                currentData = self.savePool.get()
                self.databaseObject.writeToTable('msg_relation', currentData)
                print('Save message relation successfully!')
            except Exception as e:
                print('Save message relation failed: %s!' % e)

class UserMsgIndexSaver(BaseSaver):
    def __init__(self, pool) -> None:
        super().__init__(pool)
    
    def run(self):
        while True:
            try:
                currentData = self.savePool.get()
                self.databaseObject.writeToTable('user_msg_index', currentData)
                print('Save user message index successfully!')
            except Exception as e:
                print('Save user message index failed: %s!' % e)

class UserRelationSaver(BaseSaver):
    def __init__(self, pool) -> None:
        super().__init__(pool)
    
    def run(self):
        while True:
            try: 
                currentData = self.savePool.get()
                self.databaseObject.writeToTable('user_relation', currentData)
                print('Save user relation successfully!')
            except Exception as e:
                print('Save user relation failed: %s!' % e)







