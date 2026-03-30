from ml_engine.region_detection.region_service import RegionService
from ml_engine.pipelines.trend_pipeline import TrendPipeline

class RegionTrendPipeline:

    def __init__(self):
        self.region_service = RegionService()
        self.trend_pipeline = TrendPipeline()


    def run(self, raw_texts, target_state,
        prev_counts=None, prev_velocities=None):

        target_state = target_state.lower().strip()

        tagged_posts = []

        for text in raw_texts:
            region_data = self.region_service.detect(text)

            tagged_posts.append({
                "text": text,
                "regions": region_data.get("regions", [])
            })

        filtered_texts = [
            p["text"]
            for p in tagged_posts
            if target_state in [r.lower() for r in p["regions"]] 
            or len(p["regions"]) == 0   # 🔥 fallback
        ]

        if not filtered_texts:
            filtered_texts = raw_texts

        results = self.trend_pipeline.run(
            filtered_texts,
            prev_counts,
            prev_velocities
        )

        return results[:10]