"""
trend_service.py — Serves global trending topics from ml_trend_results.

Queries the most recent ML pipeline run and returns the top N topic
clusters ranked by composite trend score (volume + velocity + acceleration
+ sentiment).
"""

from sqlalchemy import text
from app.db.connection import SessionLocal
from app.models.ml_trend_result import MLTrendResult


def get_trends(limit: int = 10):
    """
    Return the top trending topic clusters from the latest ML run.

    Each entry includes keywords, trend score, sentiment breakdown,
    volume, and contributing subreddits so the frontend can render
    rich trend cards and charts.
    """
    db = SessionLocal()
    try:
        # Find the timestamp of the most recent ML run
        latest_run = db.execute(
            text("SELECT MAX(run_at) FROM ml_trend_results")
        ).scalar()

        if latest_run is None:
            # ML pipeline hasn't run yet — return an empty list with a hint
            return {"trends": [], "message": "No ML results yet. Run the data pipeline first."}

        # Fetch top clusters from that run, ordered by composite score DESC
        data = (
            db.query(MLTrendResult)
            .filter(MLTrendResult.run_at == latest_run)
            .order_by(MLTrendResult.score.desc())
            .limit(limit)
            .all()
        )

        trends = []
        for item in data:
            trends.append({
                "topic_id":        item.topic_id,
                "keywords":        item.keywords,
                "score":           round(item.score or 0, 2),
                "volume":          item.volume,
                "velocity":        round(item.velocity or 0, 2),
                "acceleration":    round(item.acceleration or 0, 2),
                "sentiment":       round(item.sentiment or 0, 3),
                "sentiment_label": item.sentiment_label,
                "positive_pct":    round(item.positive_pct or 0, 1),
                "negative_pct":    round(item.negative_pct or 0, 1),
                "neutral_pct":     round(item.neutral_pct or 0, 1),
                "top_posts":       item.top_posts,
                "subreddits":      item.subreddits,
                "avg_ups":         round(item.avg_ups or 0, 1),
                "avg_comments":    round(item.avg_comments or 0, 1),
                "run_at":          item.run_at.isoformat() if item.run_at else None,
            })

        return {"trends": trends, "run_at": latest_run.isoformat() if latest_run else None}

    finally:
        db.close()