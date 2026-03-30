from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

class Normalizer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()

    def remove_stopwords(self, tokens):
        return [word for word in tokens if word not in self.stop_words]

    def stem(self, tokens):
        return [self.stemmer.stem(word) for word in tokens]

    def normalize(self, tokens):
        tokens = self.remove_stopwords(tokens)
        tokens = self.stem(tokens)
        return tokens