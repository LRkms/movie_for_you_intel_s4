import pandas as pd
import re

from Tools.scripts.objgraph import ignore
from konlpy.tag import Okt
# from konlpy.tag import Mecab
# # Mecab 초기화
# mecab = Mecab('C:/mecab/share/mecab-ko-dic')

df = pd.read_csv('./cleaned_data/movie_reviews.csv')
df.info()
print(df.head())

# mecab = Mecab()
okt = Okt()
cleaned_sentences = []
for review in df.reviews:
    review = re.sub('[^가-힣]', ' ', review)
    tokened_review = okt.pos(review, stem=True)
    # print(tokened_review)
    df_token = pd.DataFrame(tokened_review, columns=['word', 'class'])
    # print(df_token)
    df_token = df_token[(df_token['class'] == 'Noun') |
                        (df_token['class'] == 'Adjective') |
                        (df_token['class'] == 'Verb')]
    # print(df_token)
    words = []
    for word in df_token.word:
        if 1 < len(word):
            words.append(word)
    cleaned_sentence = ' '.join(words)
    print(cleaned_sentence)
    cleaned_sentences.append(cleaned_sentence)
df['reviews'] = cleaned_sentences
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)
df.info()
df.to_csv('./cleaned_data/cleaned_reviews.csv', index=False)

df = pd.read_csv('./cleaned_data/cleaned_reviews.csv')
df.dropna(inplace=True)

