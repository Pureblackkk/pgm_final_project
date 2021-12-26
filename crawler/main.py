from savers.saver_factory import SaverFactory
from crawlers.crawler_factory import CrawlerFactory
import yaml
from util import PoolFactory, BlogDataBase
import pandas as pd

def reInitialUser(count=None):
    blogDatabase = BlogDataBase()
    # findSql = 'SELECT follow_id FROM user_relation'
    findSql = 'SELECT uid FROM user_info'
    blogDatabase.cursor.execute(findSql)
    initialUserPool = blogDatabase.cursor.fetchall()
    finalUserList = []

    # Select valid user
    if count:
        userCount = 0
        for user in initialUserPool:
            if userCount > count:
                break

            if not blogDatabase.checkIfExists('msg_info', 'uid', user[0]):
                userCount += 1
                finalUserList.append(user[0])
    else:
        for user in initialUserPool:
            if not blogDatabase.checkIfExists('msg_info', 'uid', user[0]):
                finalUserList.append(user[0])
    
    finalUserList.reverse()
    blogDatabase.db.close()
    return finalUserList

def getInitialFromCsv(path):
    dataframe = pd.read_csv(path, encoding='utf-16')
    return dataframe['uid'].tolist()
    

if __name__ == '__main__':
    pools = PoolFactory().makePools()

    # Initial user
    # for uid in reInitialUser(300):
    #     pools['uid'].put(uid)
    for uid in getInitialFromCsv('./agent/initial_user.csv'):
        pools['uid'].put(uid)

    # Start saver threads
    SaverFactory().startSaverThreads(2, pools)

    # Start crawler threads
    CrawlerFactory(pools).startCrawlerThreads(5)

