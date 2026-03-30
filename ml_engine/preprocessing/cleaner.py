import re

class TextCleaner:
    
    def remove_urls(self, text: str) -> str:
        return re.sub(r"http\S+|www\S+", "", text)

    def remove_mentions(self, text: str) -> str:
        return re.sub(r"@\w+", "", text)

    def clean_hashtags(self, text: str) -> str:
        return re.sub(r"#(\w+)", r"\1", text)

    def remove_special_chars(self, text: str) -> str:
        return re.sub(r"[^a-zA-Z0-9\s]", "", text)

    def remove_extra_spaces(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def clean(self, text: str) -> str:
        text = self.remove_urls(text)
        text = self.remove_mentions(text)
        text = self.clean_hashtags(text)
        text = self.remove_special_chars(text)
        text = self.remove_extra_spaces(text)
        return text.lower()