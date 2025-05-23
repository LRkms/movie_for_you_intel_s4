import pandas as pd
import re
from konlpy.tag import Mecab

# Mecab 초기화
mecab = Mecab('C:/mecab/share/mecab-ko-dic')

df = pd.read_csv('./cleaned_data/movie_reviews.csv')
df.info()
print(df.head())

cleaned_sentences = []

for review in df.reviews:
    review = re.sub('[^가-힣]', ' ', review)
    tokened_review = mecab.pos(review)

    df_token = pd.DataFrame(tokened_review, columns=['word', 'class'])
    df_token = df_token[
        (df_token['class'].isin(['NNG', 'NNP', 'VA', 'VV']))]

    words = []
    for word in df_token.word:
        if 1 < len(word):
            words.append(word)
    cleaned_sentence = ' '.join(words)
    print(cleaned_sentence)
    cleaned_sentences.append(cleaned_sentence)
df['reviews'] = cleaned_sentences
df.dropna(inplace=True)
df.info()
df.to_csv('./cleaned_data/cleaned_reviews_1.csv', index=False)



