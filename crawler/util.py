import pymysql
import queue
from datetime import datetime, timezone

class BlogDataBase:
    def __init__(self) -> None:
        self.db = self._initConnect()
        self.cursor = self.db.cursor()
    
    def checkIfExists(self, table, column, key):
        sql = "SELECT * FROM %s WHERE %s = '%s'" % (table, column, key)
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return True if result else False

    def _initConnect(self):
        db = pymysql.connect(
            host='localhost',
            user='root',
            password='Barcelona10',
            database='blog'
        )
        print('------ Database connect successfully! ------')

        return db
    
    def writeToTable(self, table, dataDict):
        placeholders = ', '.join(['%s'] * len(dataDict))
        columns = ', '.join(dataDict.keys())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, placeholders)
        self.cursor.execute(sql, list(dataDict.values()))
        self.db.commit()
    
class Pool:
    def __init__(self, type: str) -> None:
        self.type = type
        self.queue = queue.Queue(10000)
    
    def get(self):
        return self.queue.get()

    def put(self, data):
        self.queue.put(data)

class PoolFactory:
    def makePools(self):
        poolNameList = [
            'uid',
            'user',
            'msg',
            'url',
            'topic',
            'msgRelation',
            'userMsg',
            'userRelation',
        ]

        poolDict = {}
        for poolName in poolNameList:
            poolDict[poolName] = Pool(poolName)

        return poolDict

def convertTimeToStamp(timeStr):
    dt = datetime.strptime(timeStr, '%a %b %d %H:%M:%S %z %Y')
    timeStamp = dt.timestamp()
    return int(timeStamp)