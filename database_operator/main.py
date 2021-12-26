from database import BlogDataBase
if __name__ == '__main__':
    blogDatabase = BlogDataBase()

    # Get blog msg content
    # outputPath = '../../data/content_marker/msg.csv'

    # Get limited blog msg
    # outputPath = '../../data/text_similarity/msg_150000.csv'

    # blogDatabase.getMsgContent(150000, outputPath)

    # # Get user relation
    # outputPath = '../../data/graph_partition/user_relation.csv'
    # blogDatabase.getUserRelation(outputPath)

    # Get whole data base
    outputPath = '../../data/database/'
    blogDatabase.saveDatabaseAsCsv(outputPath)

    # # Get edge uid
    # outputPath = '../crawler/agent/initial_user.csv'
    # blogDatabase.getNetworkEdgeUid(outputPath)

    # Get most retweeted tweets
    # outputPath = '../../data/message_selection/message_spread.csv'
    # blogDatabase.getMostRepostMsg(outputPath)
    