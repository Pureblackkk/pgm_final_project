from os import error
import pandas as pd


STOP_WORD_SET = set()
with open('../../data/stop_words.txt', 'r') as f:
    words = f.readlines()
    for word in words:
        word = word.strip('\n')
        STOP_WORD_SET.add(word)

def removeStopWords(wordList: list):
    '''
    Remove stop words from given word list
    '''
    return [word for word in wordList if not word in STOP_WORD_SET ]


class DatasetSpliter:
    def __init__(self, dataPath) -> None:
        self.dataPath = dataPath
        self.dataframe = pd.read_csv(dataPath, encoding='utf-16', sep='\t')
        # self.dataframe = pd.read_csv(dataPath, encoding='utf-8', sep=',')

    def _getSplitRatio(self, ratios: str) -> list:
        ratioList = ratios.split(':')
        return [int(ratio) for ratio in ratioList]

    def split(self, ratios='7:2:1', outputPathList=None):
        if not outputPathList:
            error('Please input the output path list')
        
        # Get ratio list
        ratioList = self._getSplitRatio(ratios)

        # Split data set
        totalLen = len(self.dataframe)
        trainLen = int(totalLen * float(ratioList[0]) / sum(ratioList))
        validLen = int(totalLen * float(ratioList[1]) / sum(ratioList))
        testLen = totalLen - trainLen - validLen

        # Make data frame list
        outputDataList = []
        outputDataList.append(self.dataframe.iloc[:trainLen])
        outputDataList.append(self.dataframe.iloc[trainLen:validLen])
        outputDataList.append(self.dataframe.iloc[validLen:])

        # Save the new data
        for i in range(len(outputPathList)):
            outputDataList[i].to_csv(outputPathList[i], index=False, encoding='utf-16')

    