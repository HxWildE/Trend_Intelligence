from .sentiment_model import SentimentModel

class SentimentInference:

    def __init__(self):
        self.model = SentimentModel()

    def analyze(self, text: str):
        return self.model.predict(text)