from re import X
from gensim import models
from gensim.models import word2vec
import pandas as pd
import numpy as np
import jieba

STOP_WORD_SET = set()
with open('../../data/stop_words.txt', 'r') as f:
    words = f.readlines()
    for word in words:
        word = word.strip('\n')
        STOP_WORD_SET.add(word)

class MyCorpus:
    def __init__(self, inputPath) -> None:
        self.dataframe = pd.read_csv(inputPath, encoding='utf-16')

    def _tokenize(self, word):
        token = jieba.lcut(str(word))
        token = [word for word in token if word not in STOP_WORD_SET]
        return token

    def __iter__(self):
        # Make tokens vector
        for message in self.dataframe['message']:
            yield self._tokenize(message)

def makeWord2VecModel(inputPath, outputPath):
    # Make corpus object
    corpus = MyCorpus(inputPath)

    # Train word2vec
    model = word2vec.Word2Vec(corpus, min_count=5)

    # Save model
    model.save(outputPath)

class MyWord2Vec:
    def __init__(self, modelPath) -> None:
        self.model = models.Word2Vec.load(modelPath)
    
    def convertWord(self, word):
        word = jieba.lcut(str(word))
        word = [x for x in word if x not in STOP_WORD_SET]

        if len(word) == 0:
            return []
            
        wordVectors = []
        for x in word:
            try:
                vec = self.model.wv[x]
                wordVectors.append(vec)
            except:
                continue
        if len(wordVectors):
            wordVectors = np.array(wordVectors)
            return np.mean(wordVectors, axis=0)
        else:
            return []
    
    def getTextSimilarity(self, pair):
        sentenceL = pair[0]
        sentenceR = pair[1]

        if not sentenceL or not sentenceR:
            return 0.0

        # Tokenize each word
        sentenceL = jieba.lcut(str(sentenceL))
        sentenceL = [word for word in sentenceL if word not in STOP_WORD_SET]
        sentenceR = jieba.lcut(str(sentenceR))
        sentenceR = [word for word in sentenceR if word not in STOP_WORD_SET]

        # Get word vector
        sentenceLVectors = np.array([self.model.wv[word] for word in sentenceL])
        sentenceRVectors = np.array([self.model.wv[word] for word in sentenceR])

        # Get mean vector
        sentenceLMeanVector = np.mean(sentenceLVectors, axis=0)
        sentenceRMeanVector = np.mean(sentenceRVectors, axis=0)

        # Calculate the cos similarity
        temp1 = np.dot(sentenceLMeanVector, sentenceLMeanVector)
        temp2 = np.dot(sentenceRMeanVector, sentenceRMeanVector)

        if temp1 and temp2:
            return np.dot(sentenceLMeanVector, sentenceRMeanVector) / (np.sqrt(temp1) * np.sqrt(temp2))
        else:
            return 0

if __name__ == '__main__':
    # # Create word2Vect model
    # inputPath = '../../data/text_similarity/msg_150000_preprocess.csv'
    # outputPath = './model/blog_150000.model'

    # makeWord2VecModel(inputPath, outputPath)

    # Calculate similarity
    testList = ('今天辛苦了一天真的很开心', '今天真的好快乐')


    modelPath = './model/blog_150000.model'
    myWord2Vec = MyWord2Vec(modelPath)
    print(myWord2Vec.getTextSimilarity(testList))