from msg_preprocess import MsgPrepocessor

if __name__ == '__main__':
    # inputFile = '../../data/content_marker/msg.csv'
    # outputFile = '../../data/content_marker/msg_preprocess_formarker_0-5000.csv'

    inputFile = '../../data/text_similarity/msg_150000.csv'
    outputFile = '../../data/text_similarity/msg_150000_preprocess.csv'

    messagePrepocessor = MsgPrepocessor(inputFile, outputFile)
    messagePrepocessor.run()

    # # Split file
    # inputFile = '../../data/content_marker/msg_preprocess_formarker_0-5000.csv'
    # outputFile = '../../data/content_marker/msg_preprocess_formarker_split'
    # messagePrepocessor = MsgPrepocessor(inputFile, outputFile)
    # messagePrepocessor.splitCsv(10000)