import re

class PreprocessingPipeline:

    def clean_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"http\S+", "", text)     # remove links
        text = re.sub(r"[^a-z\s]", "", text)    # remove symbols
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def run(self, texts):
        return [self.clean_text(t) for t in texts]