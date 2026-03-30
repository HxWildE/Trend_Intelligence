from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

class SentimentModel:

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def predict(self, text: str):
        scores = self.analyzer.polarity_scores(text)

        compound = scores['compound']      

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "label": label,
            "score": compound,
            "details": scores
        }