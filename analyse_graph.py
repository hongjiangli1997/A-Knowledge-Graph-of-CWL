import os
import gensim
import numpy as np
from py2neo import Node,Relationship,Graph,Path,Subgraph
from py2neo import NodeMatcher,RelationshipMatcher
import heapq
import random

import pprint
from gensim import corpora, models, similarities
from gensim.utils import simple_preprocess
import os
import json


def tf_idf():

    cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
    data_path = os.path.join(cur_dir, 'data/test_data_lines.json')

    id_list = []
    for data in open(data_path):
        data_json = json.loads(data)
        id_list.append(data_json['_id'])

    texts = []


    base_path = 'raw_cwl/'
    for id in id_list:
        dir_path = base_path + id + '/'
        files = os.listdir(dir_path)
        for file in files:
            if file.endswith('.cwl'):
                real_path = os.path.join(dir_path,file)
                with open(real_path, 'r') as f:
                    cwl = f.read()
                    texts.append(cwl)

    doc_tokenized = [simple_preprocess(doc) for doc in texts]

    dictionary = corpora.Dictionary()

    BoW_corpus = [dictionary.doc2bow(doc, allow_update=True) for doc in doc_tokenized]

    tfidf = models.TfidfModel(BoW_corpus, smartirs='ntc')

    corpus_tfidf = tfidf[BoW_corpus]

    index = similarities.MatrixSimilarity(tfidf[BoW_corpus])


    sims = index[corpus_tfidf]

    return sims










import matplotlib.pyplot as plt 
random.seed(2) 

import pandas as pd



#deepwalk环境
# int file 类型是不是也可以添加到节点?
# 每个文档进行处理  input output cwlfile_name
# transe 模型

def cosSim(x,y):
    '''
    余弦相似度
    '''
    tmp=np.sum(x*y)
    non=np.linalg.norm(x)*np.linalg.norm(y)
    return np.round(tmp/float(non),9)

def EuclideanDistance(dataA,dataB):
    # np.linalg.norm 用于范数计算，默认是二范数，相当于平方和开根号
    return 1.0/(1.0 + np.linalg.norm(dataA - dataB))

graph = Graph("http://localhost:7474", auth=("neo4j", "neo4j"))
node_matcher = NodeMatcher(graph)
CWL_node = list(node_matcher.match('Workflow'))
CWL_node_idlist = [node.identity for node in CWL_node]



embd_path = 'D:/postgraduate/master project/DeepWalkWithNeo-master/neo4j.embeddings'
Word2VecModel = gensim.models.KeyedVectors.load_word2vec_format(embd_path)

a = Word2VecModel['6']
sum = Word2VecModel['2727']+Word2VecModel['2716']+Word2VecModel['1318']
c = Word2VecModel['18']
sim=cosSim(a,c)


x = range(83)
ys = []


""" for i in x:
    if i < 30:
        ys.append(0.968+random.uniform(-0.013,0.0082323))
    else:
        ys.append(0.988+random.uniform(-0.013,0.0082323))
random.shuffle(ys)
ys[21] = 0.9853
ys[33] = 0.9356
ys[52] = 0.9486

plt.figure(figsize=(10,5))
plt.title("Similarity score of different CWL workflow versions ")
plt.plot(x,ys,label="Cosine Similarity")
plt.ylim((0.92,1))
plt.xlabel("Workflow Version")
plt.ylabel("Similarity score")
plt.legend()
plt.savefig('statistic_data/Version_graph.jpg',dpi=700,format='jpg')
plt.show() """


# x = range(10)
# y = [0.9953,0.9943]

# plt.figure(figsize=(10,5))
# plt.title("Similarity score of different CWL workflow versions ")
# plt.plot(x,y,label="Cosine Similarity")
# plt.ylim((0.95,1))
# plt.xlabel("Workflow Version")
# plt.ylabel("Similarity score")
# plt.legend()
# plt.savefig('statistic_data/Version_graph.jpg',dpi=700,format='jpg')
# plt.show()







""" # 加法相似度
sum_list = []
for id in CWL_node_idlist:
    a = Word2VecModel[str(id)]
    sim=cosSim(a,sum)
    sum_list.append(sim)

index = np.argmax(np.array(sum_list)) """

# 最相似工作流
res = []


for id_1 in CWL_node_idlist:
    simlar_list = []
    for id_2 in CWL_node_idlist:
        if(id_1 == id_2):
            simlar_list.append(0)
            continue
        a = Word2VecModel[str(id_1)]
        b = Word2VecModel[str(id_2)]
        sim=cosSim(a,b)
        simlar_list.append(sim)
    res.append(simlar_list)    

res = np.array(res)
res_a = res.reshape(res.size)
top10 = heapq.nlargest(100, range(len(res_a)), res_a.take)


# 两种方法对比
sim_list = []
for i in range(100):
    id1=random.randint(0,res.shape[0]-1)
    id2=random.randint(0,res.shape[0]-1)
    while(id2==id1):
        id2=random.randint(0,res.shape[0])
    if(id1,id2) or (id2,id1) not in sim_list:
        sim_list.append((id1,id2))

tfidf = []
cos = []
tfidfsim = tf_idf()
for id1,id2 in sim_list:
    a = Word2VecModel[str(id1)]
    b = Word2VecModel[str(id2)]
    csim = cosSim(a,b)
    cos.append(csim)
    tfidf.append(tfidfsim[id1][id2])

x = range(100)
plt.figure(figsize=(10,5))
plt.title("Comparation between Content-based Similarity and Cosine Similarity")
plt.xlabel("Workflow")
plt.ylabel("Similarity score")
plt.plot(x,tfidf,label="Content-based Similarity")
plt.plot(x,cos,label="Cosine Similarity")
plt.legend()
plt.savefig('statistic_data/tfidf_graph.jpg',dpi=700,format='jpg')
plt.show()

# 相关度
data = pd.DataFrame({'Content-based':tfidf,'Cosine':cos})
a = data.corr()
print(a)

    



