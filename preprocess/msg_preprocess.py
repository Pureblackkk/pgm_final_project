import re
from .base_preprocess import BasePreprocessor

class MsgPrepocessor(BasePreprocessor):
    def __init__(self, inputPath, outputPath) -> None:
        super().__init__(inputPath, outputPath)
    
    def _removeRepostTails(self, content: str):
        '''
        Remove the tails content 'xxx//xxxx//xxxx' when repost
        '''
        return content.split('//')[0]
        
    def _removeSymbols(self, content: str):
        '''
        Remove the tag symbol like '#'
        Remove the '@' symbol
        Remove the '[]' symbol
        Remove the '【】' symbol
        Remobe the '→' symbol
        ......
        '''

        content = re.sub(r'[#|\[|\]|@|【|】|\(|\)|→|¥|.|\d|」|∠|з|…|「|-|）|（|~|•|_|㊗️|❤|←|☑ |『|』|＊|~|P⃣️|^|‪‪‪‪‪—|☕|/①|②|③]', '', content)
        return content


    def _removeUrl(self, content: str):
        '''
        Remove url
        '''
        content = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', str(content), flags=re.MULTILINE)
        return content.replace('http://', '')
    
    def _removeUnseenCode(self, content:str):
        '''
        Remove unseen code \u200b
        '''
        
        return content.replace(u'\u200b', '')
    
    def _applyFunc(self, content):
        # Remove url
        content = self._removeUrl(content)

        # Remove tails 
        content = self._removeRepostTails(content)

        # Remove symbols
        content = self._removeSymbols(content)

        # Remove unseen code
        content = self._removeUnseenCode(content)

        # Remove strip
        content = content.strip()

        return content

    def run(self, start=None, end=None):
        self.dataframe['message'] = self.dataframe['message'].apply(self._applyFunc)

        # Output
        print('Prepocess successfully!')

        # Change the size
        if start and end:
            self.dataframe = self.dataframe.iloc[start:end]
        self.output()

