from os import sep
import pymysql
import csv

class BlogDataBase:
    def __init__(self) -> None:
        self.db = self._initConnect()
        self.cursor = self.db.cursor()

    def _initConnect(self):
        db = pymysql.connect(
            host='localhost',
            user='root',
            password='Barcelona10',
            database='blog'
        )
        print('------ Database connect successfully! ------')

        return db
    
    def _writeToCSV(self, col, fetchRes, path):
        outputFile = open(path, 'w', encoding='utf-16')
        myFile = csv.writer(outputFile)
        myFile.writerow(col)
        myFile.writerows(fetchRes)
        outputFile.close()

    def getMsgContent(self, num, outputPath):
        '''
        Get blog message content
        '''
        sql = 'SELECT text_content FROM msg_info LIMIT %d' % num
        self.cursor.execute(sql)
        fetchResult = self.cursor.fetchall()
        self._writeToCSV(['message'], fetchResult, outputPath)
        
    def getAllUid(self, outputPath):
        '''
        Get all the uid in user_info
        '''
        sql = 'SELECT uid from user_info' 
        self.cursor.execute(sql)
        fetchResult = self.cursor.fetchall()
        self._writeToCSV(['uid'], fetchResult, outputPath)

    def getUserRelation(self, outputPath):
        '''
        Get user relation for both user/follower/fans in uid
        '''
        sql = 'SELECT * FROM user_relation where uid in (SELECT uid FROM user_info) AND follow_id in (SELECT uid FROM user_info)'
        self.cursor.execute(sql)
        fetchResult = self.cursor.fetchall()
        self._writeToCSV(['uid', 'follow_id', 'type'], fetchResult, outputPath)
    
    def getNetworkEdgeUid(self, outputPath):
        '''
        Get edge user's id in network
        '''
        sql = 'SELECT uid FROM user_info where uid not in (SELECT uid FROM user_relation) OR uid not in (SELECT follow_id FROM user_relation)'
        self.cursor.execute(sql)
        fetchResult = self.cursor.fetchall()
        self._writeToCSV(['uid'], fetchResult, outputPath)
    
    def getMostRepostMsg(self, outputPath):
        '''
        Get most repost msg info
        '''
        sql = 'SELECT tran_user_id, tran_msg_id, COUNT(*) FROM msg_relation GROUP BY tran_user_id, tran_msg_id'
        self.cursor.execute(sql)
        fetchResult = self.cursor.fetchall()
        self._writeToCSV(['tran_user_id','tran_msg_id', 'spread'], fetchResult, outputPath)

    def saveDatabaseAsCsv(self, outputPath):
        '''
        Save all the table in database to csv
        '''
        sqlList = [
            'SELECT * FROM msg_info',
            'SELECT * FROM msg_relation',
            'SELECT * FROM topic_info',
            'SELECT * FROM url_info',
            'SELECT * FROM user_info',
            'SELECT * FROM user_msg_index',
            'SELECT * FROM user_relation'
        ]

        colNameList = [
            [
                'msg_id', 
                'uid', 
                'text_content', 
                'url_content', 
                'topic_content', 
                'type', 
                'comment_count',
                'trans_count',
                'favori_count',
                'msg_time',
            ],
            [
                'cur_user_id',
                'cur_msg_id',
                'tran_user_id',
                'tran_msg_id',
                'time_t'
            ],
            [
                'topic_id',
                'topic_content',
                'topic_count',
            ],
            [
                'url_id',
                'url_content',
                'url_domain',
            ],
            [
                'uid',
                'user_name',
                'msg_total_count',
                'fans_count',
                'follow_count',
                'tags',
                'certify_v',
                'city',
                'user_description',
            ],
            [
                'uid',
                'author_id',
                'msg_id',
                'time_t',
            ],
            [
                'uid',
                'follow_id',
                'type',
            ],
        ]

        fileNameList = [
            'msg_info',
            'msg_relation',
            'topic_info',
            'url_info',
            'user_info',
            'user_msg_index',
            'user_relation',
        ]

        for i in range(len(sqlList)):
            sql = sqlList[i]
            self.cursor.execute(sql)
            fetchResult = self.cursor.fetchall()
            self._writeToCSV(colNameList[i], fetchResult, outputPath + fileNameList[i] + '.csv')




    

