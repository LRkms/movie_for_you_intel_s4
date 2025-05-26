import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from scipy.io import mmread
import pickle
from konlpy.tag import Okt
import re
import datetime
from gensim.models import Word2Vec

def getRecommendations(cosine_sim):
    simScore = list(enumerate(cosine_sim[-1]))
    simScore = sorted(simScore, key=lambda x: x[1], reverse=True)
    simScore = simScore[:11]
    movie_idx = [i[0] for i in simScore]
    rec_movie_list = df_reviews.iloc[movie_idx, 0]
    return rec_movie_list[:11]

df_reviews = pd.read_csv('./cleaned_data/cleaned_reviews.csv')
df_reviews.info()
tfidf_matrix = mmread('./models/tfidf_movie_review.mtx').tocsr()
with open('./models/tfidf.pickle', 'rb') as f:
    tfidf = pickle.load(f)

# 영화 index를 이용한 추천
# ref_idx = 784
# print(df_reviews.iloc[ref_idx, 0])
# cosine_sim = linear_kernel(tfidf_matrix[ref_idx], tfidf_matrix)
# print(cosine_sim)
# print(len(cosine_sim[0]))
# recommendation = getRecommendations(cosine_sim)
# print(recommendation[1:])

# keyword를 이용한 추천
embedding_model = Word2Vec.load('./models/word2vec_movie_review.model')
keyword = '어벤져스'
sim_word = embedding_model.wv.most_similar(keyword, topn=10)
words = [keyword]
for word, _ in sim_word:
    words.append(word)
sentence = []
count = 10

for word in words:
    sentence = sentence + [word] * count
    count -= 1
sentence = ' '.join(sentence)
print(sentence)

sentence_vec = tfidf.transform([sentence])
cosine_sim = linear_kernel(sentence_vec, tfidf_matrix)
recommendations = getRecommendations(cosine_sim)
print(recommendations[:10])