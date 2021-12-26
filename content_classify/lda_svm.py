from .util import DatasetSpliter
from .util import STOP_WORD_SET
from gensim import corpora, models
import gensim
import jieba
import pickle
import json
import pandas as pd
import numpy as np
from sklearn.svm import LinearSVC,SVC
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report


class LdaSvm(DatasetSpliter):
    def __init__(self, dataPath) -> None:
        super().__init__(dataPath)
    
    def preprocess(self, save=True):
        # Make text vector matrix
        tokensList = []
        self.dataframe['message'].apply(lambda x: tokensList.append(jieba.lcut(str(x))))

        # Make dictionary
        self.dictionary = corpora.Dictionary(tokensList)

        # Filter invalid tokens
        stopWordId = [self.dictionary.token2id[stopword] for stopword in STOP_WORD_SET if stopword in self.dictionary.token2id]
        onceWordId = [tokenid for tokenid, docfreq in self.dictionary.dfs.items() if docfreq <= 2]
        self.dictionary.filter_tokens(stopWordId + onceWordId)

        # Filter empty word id
        self.dictionary.compactify()

        # Make tokens to vector
        self.corpus = [self.dictionary.doc2bow(tokens) for tokens in tokensList]

        # Make label vector
        self.labelList = pd.unique(self.dataframe['type']).tolist()
        self.labelDict = {}
        index = 0
        
        for item in self.labelList:
            self.labelDict[item] = index
            index +=1

        self.labelVectors = []
        # self.dataframe['type'].apply(lambda x: self.labelVectors.append([1 if label == x else 0 for label in labelList]))
        self.dataframe['type'].apply(lambda x: self.labelVectors.append([self.labelDict[x]]))

        if save:
            # Save dictionary
            modelPath = "./model/word_dictionary.dict"
            self.dictionary.save(modelPath)

            # Save corpus
            corpusPath = "./model/corpus.mm"
            corpora.MmCorpus.serialize(corpusPath, self.corpus)

            # Save label and label vecot
            labelPath = "./model/label"
            labelVectorPath = "./model/label_vector"
            file1 = open(labelPath, 'w')
            file1.write(', '.join(list(self.labelList)))
            file1.close()

            file2 = open(labelVectorPath, 'wb')
            file2.write(pickle.dumps(np.array(self.labelVectors)))
            file2.close()
    
    def LDA(self, **kwargs):
        '''
        Using LDA model
        '''
        # Parse argument
        topicNum = kwargs['topicNum']
        chunksize = kwargs['chunksize']
        passes = kwargs['passes']
        iterations = kwargs['iterations']
        save = kwargs['save'] if 'save' in kwargs else None

        for num in topicNum:
            self.ldaModel = models.LdaModel(
                corpus=self.corpus,
                id2word=self.dictionary,
                chunksize=chunksize,
                alpha='auto',
                eta='auto',
                iterations=iterations,
                num_topics=num,
                passes=passes,
                eval_every=None
            )

            corpusTopic = self.ldaModel[self.corpus]

            # Get class - topic distribution matrix
            classTopicMatrix = gensim.matutils.corpus2dense(corpusTopic, num_terms=num).T

            # Save each matrix
            path = './model/topic_%s' % (str(num))
            serilizedMatrix = pickle.dumps(classTopicMatrix)
            writer = open(path, 'wb')
            writer.write(serilizedMatrix)
            writer.close()

            # Save lda model
            if save:
                ldaPath = './model/lda_%s.model' % (str(num))
                self.ldaModel.save(ldaPath)

    
    def SVM(self, **kwargs):
        # Parse parameters 
        topicNum = kwargs['topicNum']

        # Load label vector matrix
        labelFile = open('./model/label_vector', 'rb')
        labelVector = labelFile.read()
        labelVector = pickle.loads(labelVector).flatten()

        with open('./model/best_params.json', 'w') as bestParamFile:
            for num in topicNum:
                kf = KFold(n_splits=3, shuffle=True)
                
                # Load class topic matrix
                topicFile = open('./model/topic_'+str(num), 'rb')
                classTopicMatrix = topicFile.read()
                classTopicMatrix = pickle.loads(classTopicMatrix)
                topicFile.close()

                # Train the model
                foldId = 1
                for trainIndex, testIndex in kf.split(classTopicMatrix):
                    xTrain, xTest = classTopicMatrix[trainIndex], classTopicMatrix[testIndex]
                    yTrain, yTest = labelVector[trainIndex], labelVector[testIndex]

                    # Make parameter dict
                    cRange = range(1, 11, 1)
                    penaltyRange=['l1','l2']
                    paramGrid = dict(C=cRange, penalty=penaltyRange)

                    # Define model 
                    svm = LinearSVC(C=1, penalty='l1', dual=False, tol=1e-4)
                    svmGrid = GridSearchCV(svm, paramGrid, cv=2)

                    # Save cross validation result
                    svmGrid.fit(xTrain, yTrain)
                    cvResult = pd.DataFrame.from_dict(svmGrid.cv_results_)
                    cvParamResultPath = './model/param_result_topic_%s_fold_%s' % (str(num), str(foldId))
                    cvResult.to_csv(cvParamResultPath)

                    # Save the best params
                    bestParams = json.dumps([svmGrid.best_params_, num])
                    bestParamFile.write(bestParams)

                    # Get the best model
                    bclf = svmGrid.best_estimator_  
                    bclf.fit(xTest, yTest)
                    predict = bclf.predict(xTest)
                    print("++++++++++++++++++++the number of topic are %d" % num)
                    print(classification_report(yTest, predict))

                    bestPath = './model/best_model_topic_%s_fold_%s' % (str(num), str(foldId))
                    # Save the best model result
                    bclfReportDataframe = pd.DataFrame(classification_report(yTest, predict, output_dict=True)).transpose()
                    bclfReportDataframe.to_csv(bestPath + '_report.csv')

                    # Save the best model itself
                    bestmodelFile = open(bestPath, 'wb')
                    bestmodelFile.write(pickle.dumps(bclf))
                    bestmodelFile.close()
                    foldId += 1

class LdaSvmPredict:
    def __init__(self, **param) -> None:
        self._init(param)
    
    def _init(self, param):
        '''
        Init environment needed
        '''
        # Init LDA model
        ldaPath = param['ldaPath']
        self.ldaModel = models.LdaModel.load(ldaPath)

        # Init dictionary
        dictionaryPath = param['dictionaryPath']
        self.dictionary = corpora.Dictionary.load(dictionaryPath)

        # Init svm model path
        svmModelPath = param['modelPath'] 
        svmModelFile = open(svmModelPath, 'rb')
        svmModel = svmModelFile.read()
        self.svmModel = pickle.loads(svmModel)
        svmModelFile.close()

        # Init best topic num
        self.bestTopicNum = param['bestTopicNum']

        # Init label
        labelPath = param['labelPath']
        labelFile = open(labelPath, 'r')
        self.labelList = labelFile.read().split(', ')
        labelFile.close()
    
    def filePredict(self, **param):
        '''
        Predict result from given model and file
        '''
        filePath = param['filePath']
        outputPath = param['outputPath']

        # Prepocess the file
        dataframe = pd.read_csv(filePath, encoding='utf-16')

        # Make text vector matrix
        tokensList = []
        dataframe['message'].apply(lambda x: tokensList.append(
            [token for token in jieba.lcut(str(x)) if token not in STOP_WORD_SET]
        ))

        # Convert text vector to topic vector
        corpus = [self.dictionary.doc2bow(tokens) for tokens in tokensList]
        corpusTopic = self.ldaModel[corpus]
        classTopicMatrix = gensim.matutils.corpus2dense(corpusTopic, num_terms=self.bestTopicNum).T

        # Predict
        predictResult = self.svmModel.predict(classTopicMatrix)

        # Write to new csv
        dataframe['type'] = [self.labelList[res] for res in predictResult]
        dataframe.to_csv(outputPath, index=False, encoding='utf-16', sep='\t')
    
    def singlePredict(self, word):
        tokensList = []
        tokensList.append(
            [token for token in jieba.lcut(str(word)) if token not in STOP_WORD_SET]
        )

        # Convert text vector to topic vector
        corpus = [self.dictionary.doc2bow(tokens) for tokens in tokensList]
        corpusTopic = self.ldaModel[corpus]
        classTopicMatrix = gensim.matutils.corpus2dense(corpusTopic, num_terms=self.bestTopicNum).T

        # Predict
        predictResult = self.svmModel.predict(classTopicMatrix)

        return [self.labelList[res] for res in predictResult]
   
if __name__ == '__main__':
    inputPath = '../../data/content_marker/msg_preprocess_formarker_0-50000_train.csv'
    topicNum = range(10, 201, 10)

    test = LdaSvm(inputPath)
    # test.preprocess()
    
    # test.LDA(
    #     topicNum=topicNum,
    #     chunksize=2000,
    #     passes=10,
    #     iterations=400,
    #     save=True
    # )

    # test.SVM(
    #     topicNum=topicNum
    # )


    predictor = LdaSvmPredict(
        bestTopicNum=130,
        modelPath='./model/best_model_topic_130_fold_1',
        ldaPath='./model/lda_130.model',
        dictionaryPath='./model/word_dictionary.dict',
        labelPath='./model/label',
    )

    predictor.filePredict(
        filePath='../../data/content_marker/msg_preprocess_formarker_split_start_10000_end_20000.csv',
        outputPath='../../data/content_result/msg_formarker_result_start_10000_end_20000.csv',
    )