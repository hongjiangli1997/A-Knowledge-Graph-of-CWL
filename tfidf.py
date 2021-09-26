import gensim
import pprint
from gensim import corpora, models, similarities
from gensim.utils import simple_preprocess
import os
import json
import numpy as np

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



