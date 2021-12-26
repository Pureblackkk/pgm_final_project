import pandas as pd
import networkx as nx
from networkx.algorithms import community
import matplotlib.pyplot as plt 
import metis
import pickle

COLOR_LIST = [
    'salmon',
    'peru',
    'darkorange',
    'gold',
    'olive',
    'yellowgreen',
    'lightgreen',
    'g',
    'turquoise',
    'cyan',
    'deepskyblue',
    'royalblue',
    'slateblue',
    'darkorchid',
    'hotpink',
    'crimson',
    'lightpink',
    'cornsilk',
    'linen',
    'teal',
    'turquoise',
    'yellowgreen',
    'darkgray',
    'bisque',
    'aqua',
    'gainsboro',
    'honeydew',
    'lavenderblush',
    'magenta',
    'moccasin',
]

class MakeGraph:
    def __init__(self, **kwargs) -> None:
        # Parse type
        loadType = kwargs['type']
        path = kwargs['path']

        if loadType == 'csv':
            self.relationDataframe = pd.read_csv(path, encoding='utf-16')
        elif loadType == 'model':
            self.G = nx.read_adjlist(path)

    def makeGraph(self):
        # Create Graph
        self.G = nx.Graph()

        # Add Node
        nodeSet = set(self.relationDataframe['uid'].tolist() + self.relationDataframe['follow_id'].tolist())
        print('Unique node:', len(nodeSet))
        for node in nodeSet:
            self.G.add_node(node)
        
        # Add Edge
        for item in self.relationDataframe.iterrows():
            self.G.add_edge(item[1]['uid'], item[1]['follow_id'])
    
        print('------ Graph Done ------')
    
    def graphPartition(self, npart, isDraw=False):
        '''
        Use METIS to do the graph partition
        '''
        metisNetwork = metis.networkx_to_metis(self.G)
        (edgecuts, parts) = metis.part_graph(metisNetwork, npart, recursive=True)

        # Get group list
        tempNodeUidList = list(self.G.nodes())
        self.groupNodeDict = {}

        for index, part in enumerate(parts):
            self.groupNodeDict[str(tempNodeUidList[index])] = part

        # Save group result
        with open('./model/partion_%s.dict' % (str(npart)), 'wb') as f:
            f.write(pickle.dumps(self.groupNodeDict))

        # Draw new graph
        if isDraw:
            colorList = []
            for node in self.G.nodes():
                colorList.append(COLOR_LIST[self.groupNodeDict[str(node)]])
            self.draw(colorList)

    def saveGraph(self, path):
        nx.write_adjlist(self.G, path)
    
    def draw(self, colorList=None, sizeList=None):
        nodeSize = None
        if sizeList:
            nodeSize = sizeList
        else:
            nodeSize = 10

        plt.figure()

        # Draw the graph G with fixed layout
        seed = 3
        pos = nx.spring_layout(self.G, seed=seed)

        nx.draw(self.G, with_labels=False, pos=pos, font_weight='bold', node_size=nodeSize, node_color=colorList) 
        plt.axis('on')

        plt.xticks([])
        plt.yticks([])
        plt.show()
        

