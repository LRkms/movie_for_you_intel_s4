import pandas as pd
import re
from konlpy.tag import Mecab

# Mecab 초기화
mecab = Mecab('C:/mecab/share/mecab-ko-dic')

df = pd.read_csv('./cleaned_data/movie_reviews.csv')
df.info()
print(df.head())

stop_words = ['영화', '감독', '연출', '배우', '하다', '보다', '있다', '없다', '되다',
              '않다', '연기','작품', '이다', '내다', '주다', '나오다', '아니다', '줄이다'
              '싶다', '많다', '짜다']

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
            if word not in stop_words:
                words.append(word)
            words.append(word)
    cleaned_sentence = ' '.join(words)
    print(cleaned_sentence)
    cleaned_sentences.append(cleaned_sentence)
df['reviews'] = cleaned_sentences
df.dropna(inplace=True)
df.info()
df.to_csv('./cleaned_data/cleaned_reviews_1.csv', index=False)



