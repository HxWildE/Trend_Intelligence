from .ner import LocationNER
from .geo_mapper import GeoMapper

class RegionService:

    def __init__(self):
        self.ner = LocationNER()
        self.mapper = GeoMapper()

    def detect(self, text):

        locations = self.ner.extract_locations(text)

        if not locations:
            return {
                "regions": [],
                "confidence": 0.0
            }

        states = [s.lower().strip() for s in self.mapper.map_location(locations)]
    
        confidence = len(states) / max(len(locations), 1)

        return {
            "regions": states,
            "confidence": round(confidence, 2)
        }