"""
region_service.py — Serves state-level trending topics from ml_trend_results.

Filters the latest ML run's topic clusters by the requested Indian state.
The ML runner stores contributing subreddit names in the `subreddits` column;
we use a case-insensitive substring match on that column so that topics
associated with a state's name or its well-known subreddits surface correctly.

Fallback: if no state-specific match is found, the top global topics for
that run are returned instead — ensuring the frontend always gets data.
"""

from sqlalchemy import text
from app.db.connection import SessionLocal
from app.models.ml_trend_result import MLTrendResult

# Map of Indian state names → known Reddit community keywords to search for.
# Extend this dict as more region-tagged data becomes available.
STATE_KEYWORDS: dict[str, list[str]] = {
    "maharashtra": ["mumbai", "pune", "maharashtra", "marathi"],
    "delhi":       ["delhi", "newdelhi", "delhincr"],
    "karnataka":   ["bengaluru", "bangalore", "karnataka", "kannada"],
    "tamil nadu":  ["chennai", "tamilnadu", "tamil"],
    "west bengal": ["kolkata", "bengal", "bengali"],
    "telangana":   ["hyderabad", "telangana"],
    "gujarat":     ["ahmedabad", "gujarat", "gujarati"],
    "rajasthan":   ["jaipur", "rajasthan"],
    "kerala":      ["kerala", "kochi", "malayalam"],
    "uttar pradesh": ["lucknow", "noida", "up", "uttarpradesh"],
}


def get_region_trends(state: str, limit: int = 10):
    """
    Return trending topic clusters relevant to the given Indian state.

    Args:
        state:  The state name as passed from the frontend (e.g. "Maharashtra").
        limit:  Maximum number of topics to return.

    Returns:
        A dict with a 'trends' list and a 'state' and 'run_at' key.
    """
    db = SessionLocal()
    try:
        state_lower = state.strip().lower()

        # Step 1 — find the most recent ML run timestamp
        latest_run = db.execute(
            text("SELECT MAX(run_at) FROM ml_trend_results")
        ).scalar()

        if latest_run is None:
            return {
                "state": state,
                "trends": [],
                "message": "No ML results yet. Run the data pipeline first.",
            }

        # Step 2 — build state-aware search keywords
        search_terms = STATE_KEYWORDS.get(state_lower, [state_lower])

        # Step 3 — query latest run, filter rows whose `subreddits` column
        # contains any of the state keywords (case-insensitive LIKE)
        base_q = (
            db.query(MLTrendResult)
            .filter(MLTrendResult.run_at == latest_run)
        )

        state_results = []
        for kw in search_terms:
            matches = (
                base_q
                .filter(MLTrendResult.subreddits.ilike(f"%{kw}%"))
                .order_by(MLTrendResult.score.desc())
                .all()
            )
            state_results.extend(matches)

        # De-duplicate (same topic_id may match multiple keywords)
        seen = set()
        unique_results = []
        for item in state_results:
            if item.topic_id not in seen:
                seen.add(item.topic_id)
                unique_results.append(item)

        # 🗑️ Removed the Global Fallback. Let states with 0 trends fail gracefully
        # so the UI can honestly report 'No data' instead of lying.

        # Step 4 — serialise results
        trends = []
        for item in unique_results[:limit]:
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

        return {
            "state":  state,
            "trends": trends,
            "run_at": latest_run.isoformat() if latest_run else None,
        }

    finally:
        db.close()