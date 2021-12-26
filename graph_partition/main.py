from make_graph import MakeGraph

if __name__ == '__main__':
    relationFilePath = '../../data/graph_partition/user_relation.csv'
    graphModelPath = './model/graph.adjlist'

    graphMaker = MakeGraph(type='csv', path=relationFilePath)
    graphMaker.makeGraph()

    # # Save the graph
    # graphMaker.saveGraph(graphModelPath)

    # Partition the graph
    graphMaker.graphPartition(30, isDraw=True)

    # Draw the graph
    # graphMaker.draw()