import sys
import pandas as pd
import pickle

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QStringListModel
from gensim.models import Word2Vec
from scipy.io import mmread
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

form_window = uic.loadUiType('./movie_recommendation.ui')[0]

class Exam(QWidget, form_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tfidf_matrix = mmread('./models/tfidf_movie_review.mtx').tocsr()
        with open('./models/tfidf.pickle', 'rb') as f:
            self.tfidf = pickle.load(f)
        self.embedding_model = Word2Vec.load('./models/word2vec_movie_review.model')
        self.df_reviews = pd.read_csv('./cleaned_data/cleaned_reviews.csv')
        self.titles = list(self.df_reviews['titles'])
        self.titles.sort()
        for title in self.titles:
            self.comboBox.addItem(title)
        model =QStringListModel()
        model.setStringList(self.titles)
        completer = QCompleter()
        completer.setModel(model)
        self.le_keyword.setCompleter(completer)
        self.comboBox.currentIndexChanged.connect(self.comboBox_slot)
        self.btn_recommendation.clicked.connect(self.btn_slot)

    def btn_slot(self):
        user_input = self.le_keyword.text()
        if user_input in self.titles:
            self.movie_title_recommendation(user_input)
        else:
            self.keyword_slot(user_input.split()[0])


    def keyword_slot(self, keyword):
        sim_word = self.embedding_model.wv.most_similar(keyword, topn=10)
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

        sentence_vec = self.tfidf.transform([sentence])
        cosine_sim = linear_kernel(sentence_vec, self.tfidf_matrix)
        recommendation = self.getRecommendations(cosine_sim)
        print(recommendation)
        recommendation = '\n'.join(recommendation[:10])
        self.lbl_recommendation.setText(str(recommendation))

    def getRecommendations(self, cosine_sim):
        simScore = list(enumerate(cosine_sim[-1]))
        simScore = sorted(simScore, key=lambda x: x[1], reverse=True)
        simScore = simScore[:11]
        movie_idx = [i[0] for i in simScore]
        rec_movie_list = self.df_reviews.iloc[movie_idx, 0]
        return rec_movie_list[:11]

    def comboBox_slot(self):
        title = self.comboBox.currentText()
        self.movie_title_recommendation(title)

    def movie_title_recommendation(self, title):
        movie_idx = self.df_reviews[self.df_reviews['titles'] == title].index[0]
        cosine_sim = linear_kernel(self.tfidf_matrix[movie_idx], self.tfidf_matrix)

        recommendation = self.getRecommendations(cosine_sim)
        recommendation = '\n'.join(recommendation[1:])
        self.lbl_recommendation.setText(str(recommendation))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = Exam()
    mainWindow.show()
    sys.exit(app.exec())