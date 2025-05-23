import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from scipy.io import mmread
import pickle
from konlpy.tag import Okt
import re
import datetime

def getRecommendations(cosine_sim):
    simScore = list(enumerate(cosine_sim[-1]))
    simScore = sorted(simScore, key=lambda x: x[1], reverse=True)
    simScore = simScore[:11]
    movie_idx = [i[0] for i in simScore]
    rec_movie_list = df_reviews.iloc[movie_idx, 0]
    return rec_movie_list[1:11]

df_reviews = pd.read_csv('./cleaned_data/cleaned_reviews.csv')
df_reviews.info()
tfidf_matrix = mmread('./models/tfidf_movie_review.mtx').tocsr()
with open('./models/tfidf.pickle', 'rb') as f:
    tfidf = pickle.load(f)

ref_idx = 745
print(df_reviews.iloc[ref_idx, 0])
cosine_sim = linear_kernel(tfidf_matrix[ref_idx], tfidf_matrix)
print(cosine_sim)

recommendation = getRecommendations(cosine_sim)
print(recommendation)