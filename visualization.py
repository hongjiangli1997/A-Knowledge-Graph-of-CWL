import matplotlib.pyplot as plt
import networkx as nx
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import numpy as np
import gensim


import py2neo 
from py2neo.database import Graph as NeoGraph



def export_neo_nodes():
    def takeFirst(elem):
        return elem[0]
    
    label_dict = {'Input':0,'Output':1,'Organization':2,'Project':3,'User':4,'Workflow':5}

    output_path = 'export_data/label.txt'
    graph = NeoGraph("http://localhost:7474", auth=("neo4j", "neo4j"))
    rels = list(graph.match())
    nodes = []
    for rel in rels:
        x, y = rel.start_node, rel.end_node

        id = int(x.identity)
        label = label_dict[str(x.labels)[1:]]
        nodes.append((id,label))

        id = int(y.identity)
        label = label_dict[str(y.labels)[1:]]
        nodes.append((id,label))

    nodes = list(set(nodes))
    nodes.sort(key=takeFirst)

    with open(output_path,'w') as f:
        for node in nodes:
            f.write(str(node[0])+' '+str(node[1])+'\n')
    





        
def read_node_label(filename, skip_head=False):
    fin = open(filename, 'r')
    X = []
    Y = []
    while 1:
        if skip_head:
            fin.readline()
        l = fin.readline()
        if l == '':
            break
        vec = l.strip().split(' ')
        X.append(vec[0])
        Y.append(vec[1:])
    fin.close()
    return X, Y


def plot_embeddings(embeddings,):
    X, Y = read_node_label('export_data/label.txt')

    emb_list = []
    for k in X:
        emb_list.append(embeddings[k])
    emb_list = np.array(emb_list)

    #model = TSNE(n_components=2)
    model = PCA(n_components=2)
    node_pos = model.fit_transform(emb_list)


    color_idx = {}
    for i in range(len(X)):
        color_idx.setdefault(Y[i][0], [])
        color_idx[Y[i][0]].append(i)

    for c, idx in color_idx.items():
        plt.scatter(node_pos[idx, 0], node_pos[idx, 1], s=7, label=c)
    plt.legend()
    plt.savefig('statistic_data/PCA_graph.jpg',dpi=700,format='jpg')
    plt.show()


if __name__ == "__main__":
    # export_neo_nodes()
    embd_path = 'D:/postgraduate/master project/DeepWalkWithNeo-master/neo4j.embeddings'
    Word2VecModel = gensim.models.KeyedVectors.load_word2vec_format(embd_path)
    embeddings = {}
    for word in Word2VecModel.index_to_key:
        embeddings[word] = Word2VecModel[word]
    plot_embeddings(embeddings)
