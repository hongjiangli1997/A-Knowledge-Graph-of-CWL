import json

import gensim
import nltk
from gensim.utils import simple_preprocess
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud
from bs4 import BeautifulSoup


import matplotlib.pyplot as plt


def sent_to_words(sentences):
    # WORDNET LEMMATIZER
    wordnet_lemmatizer = WordNetLemmatizer()
    for sentence in sentences:
        snet_list = gensim.utils.simple_preprocess(str(sentence), deacc=True)
        yield list(map(lambda x: wordnet_lemmatizer.lemmatize(x), snet_list))



total_label = []
with open('data1.json','r') as f:
    data = json.loads(f.read())
    for content in data.values():
        label = content['label']
        total_label.append(label)
    

data_words = list(sent_to_words(total_label))

unique_tweets = [t for t in data_words if t]

total_label = ''
for item in unique_tweets:
    long_string = ' '.join(item)
    total_label = total_label + ' ' + long_string

# create a WordCloud object
wordcloud = WordCloud(background_color="white", max_words=300, contour_width=3, contour_color='steelblue', width=700,
                      height=300, random_state=21 )

# generate a word cloud
wordcloud.generate(total_label)

# visualize the word cloud
image = wordcloud.to_image()
plt.imshow(image)
plt.show()




