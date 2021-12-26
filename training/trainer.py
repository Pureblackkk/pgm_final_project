import sys
import pickle
import random
import numpy as np
from networkx.algorithms.cuts import edge_expansion
from feature import FeatureCalculator
sys.path.append('..')
import torch
import torch.nn as nn
from graph_partition.make_graph import MakeGraph
        
class Trainer:
    def __init__(self) -> None:
        self._initConfig()
        self._prepareData()
        print('====== Trainer Initialization Done! ======')

    def _initConfig(self):
        self.featureCal = FeatureCalculator()
        
        # Load group dict
        self.groupPath = '../graph_partition/model/partion_30.dict'
        with open(self.groupPath, 'rb') as f:
            self.groupDict = pickle.loads(f.read())
        
        # Load Graph model
        self.modelPath = '../graph_partition/model/graph.adjlist'
        self.G = MakeGraph(type='model', path=self.modelPath).G
        self.subGMap = {}

        # Define data selection config
        self.minRepostThreshold = 5
        self.minShareThreshold = 0.15

        # Define Train:Valid:Test
        self.isValidationIncluded = False
        self.dataSplit = [0.7, 0.2, 0.1]

        # Define is shuffle
        self.isShuffle = True
        
    def _extendSample(self, sample):
        authorId = sample[0]
        msgId = sample[1]
        groupId = sample[2]
        repostUidList = sample[3]

        # Get text, url, topic, text as messageParam
        curMsgInfo = self.featureCal.metricsCal.msgInfoDF[
            self.featureCal.metricsCal.msgInfoDF['msg_id'].astype(str) == str(msgId)
        ]

        try:
            textType = curMsgInfo['text_type'].values[0]
            url = curMsgInfo['url'].values[0]
            topic = curMsgInfo['topic'].values[0]
            text = curMsgInfo['text_content'].values[0]
        except Exception as e:
            print('Author: %s, Msg Id: %s not found !!!' % (authorId, msgId))
            return None

        messageParam = {
            'textType': textType,
            'url': url,
            'topic': topic,
            'text': text,
        }

        # Get sub graph
        subGraph = None

        if groupId in self.subGMap.keys():
            subGraph = self.subGMap[groupId]
        else:
            subNodes = [k for k,v in self.groupDict.items() if str(v) == groupId]
            self.subGMap[groupId] = self.G.subgraph(subNodes)
            subGraph = self.subGMap[groupId]

            # Add repost attributes to network
            for nodeName in subGraph.nodes():
                subGraph.nodes[str(nodeName)]['repost'] = 1 if str(nodeName) in repostUidList else 0
        
        # Return new data form as AuthorId, MsgId, MessageParam, SubGraph
        return (authorId, msgId, messageParam, subGraph)
    
    def _prepareData(self):
        # Load all data 
        allData = None
        with open('../../data/final/all_data.tuple', 'rb') as f:
            allData = pickle.loads(f.read())
        
        extendedData = []
        for sample in allData:
            extendedSample = self._extendSample(sample)
            if extendedSample != None:
                extendedData.append(extendedSample)
        
        totalLen = len(extendedData)
        print('------ In total %s data' % (str(totalLen)))

        # Shuffle
        if self.isShuffle:
            random.shuffle(extendedData)

        # Split the dataset
        if self.isValidationIncluded:
            firstEnd = int(totalLen * (self.dataSplit[0]))
            secondEnd = int(totalLen * (self.dataSplit[0] + self.dataSplit[1]))
            self.trainSet = extendedData[:firstEnd]
            self.validSet = extendedData[firstEnd:secondEnd]
            self.testSet = extendedData[secondEnd:]
        else:
            firstEnd = int(totalLen * (self.dataSplit[0]))
            self.trainSet = extendedData[:firstEnd]
            self.validSet = extendedData[firstEnd:]

        # Pre-define the partition group combination
        print('lalala', len(list(self.trainSet[0][3].nodes())))
        self.groupCombination = self._getPartitionGroup(len(self.trainSet[0][3].nodes()))

    def _preparePotentiaDict(self, sample):
        authorId, msgId, messageParam, subGraph = sample
        
        infoVecDict = {}
        userVecDict = {}
        relationVecDict = {}

        # Make info and user Dict
        for node in subGraph.nodes():
            # Get info Vector
            infoVecDict[str(node)] = {
                '0': None,
                '1': None,
            }
            infoVecDict[str(node)]['0'] = self.featureCal.getInfoFeatureVector(node, msgId, 0)
            infoVecDict[str(node)]['1'] = self.featureCal.getInfoFeatureVector(node, msgId, 1)

            # Get user Vector
            userVecDict[str(node)] = {
                '0': None,
                '1': None,
            }
            userVecDict[str(node)]['0'] = self.featureCal.getUserFeatureVector(node, authorId, messageParam, 0)
            userVecDict[str(node)]['1'] = self.featureCal.getUserFeatureVector(node, authorId, messageParam, 1)

        # Make edge dict
        for edge in subGraph.edges:
            uidv = str(edge[0])
            uidw = str(edge[1])
            relationKey = uidv + ',' + uidw
            relationVecDict[relationKey] = {
                '0,0': None,
                '0,1': None,
                '1,0': None,
                '1,1': None,
            }
            relationVecDict[relationKey]['0,0'] = self.featureCal.getRelationFeatureVector(uidv, uidw, authorId, 0, 0)
            relationVecDict[relationKey]['0,1'] = self.featureCal.getRelationFeatureVector(uidv, uidw, authorId, 0, 1)
            relationVecDict[relationKey]['1,0'] = self.featureCal.getRelationFeatureVector(uidv, uidw, authorId, 1, 0)
            relationVecDict[relationKey]['1,1'] = self.featureCal.getRelationFeatureVector(uidv, uidw, authorId, 1, 1)

        return (infoVecDict, userVecDict, relationVecDict)
    
    def _getPartitionGroup(self, sampleSize):
        groupList = []

        def recursiveGet(sampleSize, preSample):
            if sampleSize == 0:
                preSample = ','.join(preSample)
                groupList.append(preSample)
                return
            preSample1 = list(preSample) + ['0']
            preSample2 = list(preSample) + ['1']
            recursiveGet(sampleSize - 1, preSample1)
            recursiveGet(sampleSize - 1, preSample2)
        
        recursiveGet(sampleSize, [])
        return groupList
    
    def run(self, epoch=1):
        # Initial Model
        model = MyModel()

        # Initial optimizer
        optimizer = torch.optim.SGD(model.parameters(), lr=1e-2, momentum=0.9)

        for e in range(epoch):
            print('==== Epoch Num: %s' % (str(e)))
            for trainData in self.trainSet:
                # Make potential dict
                potentialDict = self._preparePotentiaDict(trainData)

                # Calculate prob
                prob = model(self.groupCombination, trainData[3], potentialDict)

                # Backward
                optimizer.zero_grad()
                prob.backward()
                optimizer.step()

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.w1 = torch.nn.Parameter(torch.rand((1, 23)))
        self.w2 = torch.nn.Parameter(torch.rand((1, 3)))
    
    def _makeMatrixForPotential(self):
        # Make node Matrix
        nodeMatrix = []    
        for node in self.mySubGraph.nodes():
            currentRepost = self.mySubGraph.nodes[str(node)]['repost']
            infoVec = self.myVecDict[0][str(node)][str(currentRepost)]
            userVec = self.myVecDict[1][str(node)][str(currentRepost)]
            nodeMatrix.append(infoVec + userVec)

        # Make edge Matrix
        edgeMatrix = []
        for edge in self.mySubGraph.edges:
            uv = edge[0]
            uw = edge[1]
            uvRepost = self.mySubGraph.nodes[str(uv)]['repost']
            uwRepost = self.mySubGraph.nodes[str(uw)]['repost']
            key = uv+','+uw
            repost = str(uvRepost) + ',' + str(uwRepost)

            relationVec = self.myVecDict[2][key][repost]
            edgeMatrix.append(relationVec)
        
        nodeMatrix = torch.from_numpy(np.array(nodeMatrix).T)
        edgeMatrix = torch.from_numpy(np.array(edgeMatrix).T)
        return nodeMatrix, edgeMatrix

    def _makeMatrixForPartition(self, groupStatus):
        # Make node Matrix
        nodeMatrix = []
        nodesList = self.mySubGraph.nodes()
        repostDict = {}
        for index in range(len(nodesList)):
            currentRepost = groupStatus[index]
            nodeName = str(nodesList[index])
            repostDict[nodeName] = currentRepost

            infoVec = self.myVecDict[0][nodeName][str(currentRepost)]
            userVec = self.myVecDict[1][nodeName][str(currentRepost)]
            nodeMatrix.append(infoVec + userVec)

        # Make edge Matrix
        edgeMatrix = []
        for edge in self.mySubGraph.edges:
            uv = edge[0]
            uw = edge[1]
            uvRepost = repost[str(uv)]
            uwRepost = repost[str(uw)]
            key = uv+','+uw
            repost = str(uvRepost) + ',' + str(uwRepost)

            relationVec = self.myVecDict[2][key][repost]
            edgeMatrix.append(relationVec)
        
        nodeMatrix = torch.from_numpy(np.array(nodeMatrix).T)
        edgeMatrix = torch.from_numpy(np.array(edgeMatrix).T)
        return nodeMatrix, edgeMatrix

    def forward(self, groupList, subGraph, vecDict):
        self.myVecDict = vecDict
        self.mySubGraph = subGraph

        # Calculate potential part
        potentialNodeMatrix, potentialEdgeMatrix = self._makeMatrixForPotential()
        potentialPart1 = torch.mm(self.w1, potentialNodeMatrix)
        potentialPart2 = torch.mm(self.w2, potentialEdgeMatrix)
        potentialValue = potentialPart1 + potentialPart2

        # Calculate partition part
        exponentialVal = 0

        for group in groupList:
            partitionNodeMatrix, partitionEdgeMatrix = self._makeMatrixForPartition(group)
            partitionPart1 = torch.sum(torch.mm(self.w1, partitionNodeMatrix))
            partitionPart2 = torch.sum(torch.mm(self.w2, partitionEdgeMatrix))
            partitionPartValue = partitionPart1 + partitionPart2
            exponentialVal += torch.exp(partitionPartValue)
        
        negativeProb = torch.log(exponentialVal) - potentialValue

        return negativeProb






    