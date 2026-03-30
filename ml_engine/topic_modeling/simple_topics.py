import re

class SimpleTopicExtractor:

    def __init__(self):
        # basic keyword set (expand later)
        self.keywords = {
            "rain", "flood", "storm",
            "cricket", "ipl", "match",
            "election", "vote",
            "traffic", "accident",
            "heat", "weather"
        }

    def extract(self, text):
        words = re.findall(r"\b\w+\b", text.lower())

        topics = [w for w in words if w in self.keywords]

        return list(set(topics))