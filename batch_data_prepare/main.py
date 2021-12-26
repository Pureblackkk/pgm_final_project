from message_selection import MessageSelection

if __name__ == '__main__':
    modelPath = '../graph_partition/model/graph.adjlist'
    groupPath = '../graph_partition/model/partion_40.dict'

    messageSelector = MessageSelection(
        modelPath=modelPath,
        groupPath=groupPath
    )
    
    validData = messageSelector.getValidData(10, 0.15)
