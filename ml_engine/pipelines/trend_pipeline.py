# end-to-end processing

from ml_engine.preprocessing.pipeline import PreprocessingPipeline
from ml_engine.sentiment.inference import SentimentInference

from ml_engine.topic_modeling.embeddings import EmbeddingModel
from ml_engine.topic_modeling.clustering import ClusterModel
from ml_engine.topic_modeling.labeling import TopicLabeler
from ml_engine.region_detection.region_service import RegionService

from ml_engine.trend_detection.velocity import VelocityCalculator
from ml_engine.trend_detection.acceleration import AccelerationCalculator
from ml_engine.trend_detection.scoring import TrendScorer


class TrendPipeline:

    def __init__(self):
        self.preprocessor = PreprocessingPipeline()
        self.sentiment_model = SentimentInference()

        self.embedder = EmbeddingModel()
        self.clusterer = ClusterModel(distance_threshold=1.25)
        self.labeler = TopicLabeler()
        self.region_service = RegionService()

        self.velocity_calc = VelocityCalculator()
        self.acceleration_calc = AccelerationCalculator()
        self.scorer = TrendScorer()

    def run(self, raw_texts, metadata=None, prev_counts=None, prev_velocities=None):
        """
        Args:
            raw_texts: list of text strings
            metadata: list of dicts with keys: title, subreddit, ups, num_comments
            prev_counts: dict of {topic_id: count} from previous run
            prev_velocities: dict of {topic_id: velocity} from previous run
        """

        # handle empty input
        if not raw_texts:
            return []

        normalized_texts = []
        sentiments = []
        sentiment_labels = []

        # STEP 1: Preprocessing + Sentiment + NER
        for i, text in enumerate(raw_texts):
            processed = self.preprocessor.clean_text(text)
            normalized_texts.append(processed)

            sentiment = self.sentiment_model.analyze(text)
            sentiments.append(sentiment["score"])
            sentiment_labels.append(sentiment["label"])
            
            # 🌍 Inject Region NER dynamically
            region_data = self.region_service.detect(text)
            if region_data.get("regions") and metadata and i < len(metadata):
                detected_states = ", ".join(region_data["regions"])
                existing_sub = metadata[i].get("subreddit", "")
                if existing_sub:
                    metadata[i]["subreddit"] = f"{existing_sub}, {detected_states}"
                else:
                    metadata[i]["subreddit"] = detected_states

        # STEP 2: Embeddings
        embeddings = self.embedder.encode(normalized_texts)

        # STEP 3: Clustering
        labels = self.clusterer.fit(embeddings)

        # STEP 4: Topic Labeling
        topics = self.labeler.get_topic_labels(normalized_texts, labels)

        # STEP 5: Aggregate per topic
        topic_counts = {}
        topic_sentiment_scores = {}
        topic_sentiment_labels = {}
        topic_post_indices = {}

        for i, label in enumerate(labels):
            topic_counts[label] = topic_counts.get(label, 0) + 1
            topic_sentiment_scores.setdefault(label, []).append(sentiments[i])
            topic_sentiment_labels.setdefault(label, []).append(sentiment_labels[i])
            topic_post_indices.setdefault(label, []).append(i)

        # STEP 6: Trend Scoring + Rich Data
        results = []

        for label in topic_counts:
            # 🗑️ Junk Filter: Discard clusters with too few posts
            # A true trend needs at least 3 occurrences to prove structural significance
            if topic_counts[label] < 3:
                continue

            volume = topic_counts[label]

            prev_count = prev_counts.get(label, 0) if prev_counts else 0
            velocity = self.velocity_calc.compute(prev_count, volume)

            prev_velocity = prev_velocities.get(label, 0) if prev_velocities else 0
            acceleration = self.acceleration_calc.compute(prev_velocity, velocity)

            avg_sentiment = sum(topic_sentiment_scores[label]) / len(topic_sentiment_scores[label])

            # Sentiment breakdown
            labels_list = topic_sentiment_labels[label]
            total = len(labels_list)
            pos_count = labels_list.count("positive")
            neg_count = labels_list.count("negative")
            neu_count = labels_list.count("neutral")

            positive_pct = round((pos_count / total) * 100, 1)
            negative_pct = round((neg_count / total) * 100, 1)
            neutral_pct = round((neu_count / total) * 100, 1)

            # Determine majority sentiment label
            if pos_count >= neg_count and pos_count >= neu_count:
                majority_label = "positive"
            elif neg_count >= pos_count and neg_count >= neu_count:
                majority_label = "negative"
            else:
                majority_label = "neutral"

            # Top posts and subreddit distribution (only if metadata provided)
            top_posts_str = ""
            subreddits_str = ""
            avg_ups = 0
            avg_comments = 0

            if metadata:
                indices = topic_post_indices[label]
                cluster_meta = [metadata[i] for i in indices if i < len(metadata)]

                if cluster_meta:
                    # Top 3 posts by upvotes
                    sorted_posts = sorted(cluster_meta, key=lambda x: x.get("ups", 0), reverse=True)
                    top_titles = [p.get("title", "")[:120] for p in sorted_posts[:3] if p.get("title")]
                    top_posts_str = " || ".join(top_titles)

                    # Subreddit distribution
                    subs = list(set(p.get("subreddit", "") for p in cluster_meta if p.get("subreddit")))
                    subreddits_str = ", ".join(sorted(subs))

                    # Avg engagement
                    ups_list = [p.get("ups", 0) for p in cluster_meta]
                    comments_list = [p.get("num_comments", 0) for p in cluster_meta]
                    avg_ups = round(sum(ups_list) / len(ups_list), 1) if ups_list else 0
                    avg_comments = round(sum(comments_list) / len(comments_list), 1) if comments_list else 0

            score = self.scorer.compute_score(
                volume,
                velocity,
                acceleration,
                avg_sentiment
            )

            results.append({
                "topic_id": label,
                "keywords": topics[label],
                "volume": volume,
                "velocity": velocity,
                "acceleration": acceleration,
                "sentiment": round(avg_sentiment, 3),
                "sentiment_label": majority_label,
                "positive_pct": positive_pct,
                "negative_pct": negative_pct,
                "neutral_pct": neutral_pct,
                "top_posts": top_posts_str,
                "subreddits": subreddits_str,
                "avg_ups": avg_ups,
                "avg_comments": avg_comments,
                "score": round(score, 3)
            })

        # STEP 7: Sort by score and cap to Top 20 to keep Dashboard UI fast and polished
        ranked_trends = sorted(results, key=lambda x: x["score"], reverse=True)
        return ranked_trends[:20]


# Optional helper (safe to keep)
def run_pipeline(texts):
    pipeline = TrendPipeline()
    return pipeline.run(texts)