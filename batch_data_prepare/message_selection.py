from networkx.algorithms.centrality import group
from networkx.classes import graph
import networkx as nx
from numpy.core.fromnumeric import size
import pandas as pd
import sys
import pickle
sys.path.append('../')
from database_operator.database import BlogDataBase
from graph_partition.make_graph import MakeGraph

class MessageSelection:
    def __init__(self, **args) -> None:
        self._initArgs(args)

    def _initArgs(self, args:dict):
        # Load group dict
        groupPath = args['groupPath'] if 'groupPath' in args else None
        self.groupDict = None
        if groupPath:
            with open(groupPath, 'rb') as f:
                self.groupDict = pickle.loads(f.read())
            
        # Load graph
        modelPath = args['modelPath'] if 'modelPath' in args else None
        self.graph = None
        if modelPath:
            self.graph = MakeGraph(type='model', path=modelPath)
        
    def _getValidUid(self):
        userRelation = pd.read_csv('../../data/graph_partition/user_relation.csv', encoding='utf-16', sep=',')
        fansUidSet = set(userRelation['uid'])
        followUidSet = set(userRelation['follow_id'])
        return fansUidSet & followUidSet

    def getMessageSpread(self, minRepost):
        # Get valid uid
        validUid = self._getValidUid()

        # Read whole msg relation table
        msgRelation = pd.read_csv('../../data/database/msg_relation.csv', encoding='utf-16', sep=',')

        # Get message spread
        msgRelationValid = msgRelation[msgRelation['cur_user_id'].isin(validUid)]
        spread = msgRelationValid.groupby(['tran_user_id','tran_msg_id'], as_index=False).count()[['tran_user_id', 'tran_msg_id', 'cur_user_id']]
        spreadValid = spread[spread['cur_user_id'] >= minRepost].sort_values(by=['cur_user_id'], ascending=False)

        # Get current uid who repost this message
        def _getUidWhoRepost(uid, msg_id):
            repostUid = msgRelation[(msgRelation['tran_user_id'] == uid) & (msgRelation['tran_msg_id'] == msg_id)]['cur_user_id'].tolist()
            repostUid = [str(x) for x in repostUid]
            return repostUid
        
        resTupleList = []
        spreadValid.apply(lambda x: resTupleList.append((
            str(x['tran_user_id']), 
            str(x['tran_msg_id']), 
            _getUidWhoRepost(x['tran_user_id'], x['tran_msg_id'])
        )), axis=1)

        return resTupleList
    
    def calculateShareWithinGroup(self, idTuple, minThreshold):
        authorId, spreadIdList = idTuple
        
        # Create size dict
        sizeDict = {}
        for value in self.groupDict.values():
            sizeDict[str(value)] = sizeDict.get(str(value), 0) + 1
                
        # Define share dict
        shareDict = {}
        for node in spreadIdList:
            group = self.groupDict[str(node)]
            shareDict[str(group)] = shareDict.get(str(group), 0) + 1
        
        maxShare = 0
        maxGroup = 0

        for group in shareDict.keys():
            shareDict[group] = shareDict[group] / sizeDict[group]
            if shareDict[group] > maxShare:
                maxShare = shareDict[group]
                maxGroup = group

        print(shareDict)
        # Filter if it is valid sample
        if maxShare > minThreshold:
            # Get spread Y = 1's id in max Group
            repostUidList = []
            for node in spreadIdList:
                if self.groupDict[str(node)] == maxGroup:
                    repostUidList.append(str(node))
            return maxGroup, repostUidList
        else:
            return 'None', 'None'
        
    def drawSpread(self, idTuple):
        authorId, spreadIdList = idTuple

        # Make color List and node size
        colorList = []
        sizeList = []

        for node in self.graph.G.nodes():
            if node == authorId:
                colorList.append('red')
                sizeList.append(20)
            elif node in spreadIdList:
                colorList.append('skyblue')
                sizeList.append(15)
            else:
                colorList.append('None')   
                sizeList.append(3)

        self.graph.draw(colorList, sizeList)
    
    def getValidData(self, minRepostThreshold, minShareThreshold, isSave=True):
        '''
        Get training data
        '''
        spreadList = self.getMessageSpread(minRepostThreshold)
        validSampleList = []
        
        for sample in spreadList:
            print('Author Id: ', sample[0])
            print('Message Id: ', sample[1])

            # Filter share 
            validGroup, repostUidList = self.calculateShareWithinGroup((sample[0], sample[2]), minShareThreshold)
            if validGroup != 'None':
                validSampleList.append((sample[0], sample[1], validGroup, repostUidList))
            
            # Draw 
            self.drawSpread((sample[0], sample[2]))
        
        if isSave:
            with open('../../data/final/all_data.tuple', 'wb') as f:
                f.write(pickle.dumps(validSampleList))
            
        return validSampleList

        









        
