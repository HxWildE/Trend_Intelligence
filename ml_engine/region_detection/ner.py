import spacy
import re

class LocationNER:

    def __init__(self):
       try:
            self.nlp = spacy.load("en_core_web_sm")
       except OSError:
            raise RuntimeError(
                "spaCy model not found. Run: python -m spacy download en_core_web_sm"
            )
       
       self.known_aliases = {
            "blr", "bglr", "hyd", "mum", "del", "kol", "chn", "pnq"
        }

    def clean_word(self, word):
        return re.sub(r"[^\w\s]", "", word)

    def extract_locations(self, text):
        doc = self.nlp(text)

        locations = []

        # spaCy NER
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                locations.append(ent.text)

        # slang detection
        words = text.lower().split()

        for word in words:
            clean = self.clean_word(word)

            if clean in self.known_aliases:
                locations.append(clean)

        return list(set(locations))