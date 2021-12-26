from os import sep
import pandas as pd

class BasePreprocessor:
    def __init__(self, inputPath, outputPath) -> None:
        self.inputPath = inputPath
        self.outputPath = outputPath
        
        try:
            self.dataframe = pd.read_csv(inputPath, encoding='utf-16', sep='\t')
        except:
            self.dataframe = None
    
    def splitCsv(self, chunkSize):
        totalLen = len(self.dataframe)
        startIndex = 0

        while startIndex < totalLen:
            endIndex = startIndex + chunkSize
            self.dataframe.iloc[startIndex:endIndex].to_csv(
                self.outputPath+'_start_%s_end_%s.csv' % (startIndex, endIndex),
                index=False, 
                encoding='utf-16'
            )
            startIndex = endIndex

    def output(self):
        self.dataframe.to_csv(self.outputPath, index=False, encoding='utf-16')

