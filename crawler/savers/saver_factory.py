from .savers import UserInfoSaver, MsgInfoSaver, UrlInfoSaver, TopicInfoSaver, MsgRelationSaver, UserMsgIndexSaver, UserRelationSaver

class SaverFactory:
    def __init__(self) -> None:
        self.poolsMap = {
            'user': UserInfoSaver,
            'msg': MsgInfoSaver,
            'url': UrlInfoSaver,
            'topic': TopicInfoSaver,
            'msgRelation': MsgRelationSaver,
            'userMsg': UserMsgIndexSaver,
            'userRelation': UserRelationSaver,
        }
    
    def startSaverThreads(self, num, pools: dict):
        threads = self._makeSaverThreads(num, pools)
        for thread in threads:
            thread.start()

    def _makeSaverThreads(self, num, pools: dict):
        threadsList = []

        for name, pool in pools.items():
            if name != 'uid':
                for i in range(num):
                    threadsList.append(self.poolsMap[name](pool))

        return threadsList