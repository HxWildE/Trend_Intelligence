"""
ml_runner.py — Integration Bridge between Data Pipeline and ML Engine

Flow:
  1. Read latest posts from Postgres (reddit_trends table)
  2. Fetch previous run's data for velocity/acceleration tracking
  3. Build raw texts + metadata
  4. Run TrendPipeline (sentiment, clustering, scoring)
  5. Write enriched results to ml_trend_results table
"""

import os
import sys
from datetime import datetime, timezone

# Ensure the project root is on the path so all imports resolve correctly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import create_engine, text

from data_pipeline.config import config
from ml_engine.pipelines.trend_pipeline import TrendPipeline


def fetch_latest_posts(engine, limit=500):
    """Fetch the most recent posts from the reddit_trends table."""
    query = text("""
        SELECT title, content, subreddit, ups, num_comments, created_utc
        FROM reddit_trends
        ORDER BY processed_at DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"limit": limit})
        rows = result.fetchall()
    return rows


def fetch_previous_run(engine):
    """Fetch the most recent ML run's topic data for velocity/acceleration tracking."""
    query = text("""
        SELECT topic_id, volume, velocity
        FROM ml_trend_results
        WHERE run_at = (SELECT MAX(run_at) FROM ml_trend_results)
    """)
    prev_counts = {}
    prev_velocities = {}
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
            for row in rows:
                tid, vol, vel = row[0], row[1], row[2]
                prev_counts[tid] = vol or 0
                prev_velocities[tid] = vel or 0.0
    except Exception:
        pass  # First run — no previous data
    return prev_counts, prev_velocities


def save_results(engine, results):
    """Insert enriched ML trend results into ml_trend_results table."""
    if not results:
        print("[WARNING] ML Engine returned no results to save.")
        return

    insert_query = text("""
        INSERT INTO ml_trend_results
            (topic_id, keywords, volume, velocity, acceleration,
             sentiment, sentiment_label, positive_pct, negative_pct, neutral_pct,
             top_posts, subreddits, avg_ups, avg_comments, score, run_at)
        VALUES
            (:topic_id, :keywords, :volume, :velocity, :acceleration,
             :sentiment, :sentiment_label, :positive_pct, :negative_pct, :neutral_pct,
             :top_posts, :subreddits, :avg_ups, :avg_comments, :score, :run_at)
    """)

    run_timestamp = datetime.now(timezone.utc)
    rows_to_insert = []
    for res in results:
        rows_to_insert.append({
            "topic_id":        int(res["topic_id"]),
            "keywords":        ", ".join(res.get("keywords", [])),
            "volume":          int(res.get("volume", 0)),
            "velocity":        float(res.get("velocity", 0.0)),
            "acceleration":    float(res.get("acceleration", 0.0)),
            "sentiment":       float(res.get("sentiment", 0.0)),
            "sentiment_label": str(res.get("sentiment_label", "neutral")),
            "positive_pct":    float(res.get("positive_pct", 0)),
            "negative_pct":    float(res.get("negative_pct", 0)),
            "neutral_pct":     float(res.get("neutral_pct", 0)),
            "top_posts":       str(res.get("top_posts", "")),
            "subreddits":      str(res.get("subreddits", "")),
            "avg_ups":         float(res.get("avg_ups", 0)),
            "avg_comments":    float(res.get("avg_comments", 0)),
            "score":           float(res.get("score", 0.0)),
            "run_at":          run_timestamp,
        })

    with engine.begin() as conn:
        conn.execute(insert_query, rows_to_insert)

    print(f"[SUCCESS] ML Engine: {len(rows_to_insert)} trend topics saved to ml_trend_results.")


def run_ml_pipeline():
    """Main entry point: fetch data, run ML, store results."""
    print(f"--- [ML ENGINE] Starting at {datetime.now()} ---")

    try:
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    except Exception as e:
        print(f"[ERROR] Could not connect to Postgres: {e}")
        return

    # Step 0: Ensure all tables exist (runs schema.sql which uses IF NOT EXISTS)
    schema_path = os.path.join(PROJECT_ROOT, "database", "postgres", "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        with engine.begin() as conn:
            conn.execute(text(schema_sql))
            
            # 🧹 NEW ARCHITECTURE: 24-HOUR AUTO CLEANUP
            print("[INFO] Purging old records (>24 hours) to prevent infinite database growth...")
            conn.execute(text("DELETE FROM reddit_trends WHERE processed_at < NOW() - INTERVAL '24 hours'"))
            conn.execute(text("DELETE FROM ml_trend_results WHERE run_at < NOW() - INTERVAL '24 hours'"))
    else:
        print(f"[WARNING] Schema file not found at {schema_path}")

    # Step 1: Fetch posts
    rows = fetch_latest_posts(engine)
    if not rows:
        print("[WARNING] No posts found in reddit_trends. Skipping ML run.")
        return

    print(f"[INFO] Fetched {len(rows)} posts from Postgres for ML analysis.")

    # Step 2: Fetch previous run data for velocity tracking
    prev_counts, prev_velocities = fetch_previous_run(engine)
    if prev_counts:
        print(f"[INFO] Loaded {len(prev_counts)} topics from previous run for velocity tracking.")
    else:
        print("[INFO] No previous run data found (first run).")

    # Step 3: Build raw text inputs + metadata
    raw_texts = []
    metadata = []
    for row in rows:
        title       = row[0] or ""
        content     = row[1] or ""
        subreddit   = row[2] or ""
        ups         = row[3] or 0
        num_comments = row[4] or 0

        combined = f"{title}. {content}".strip()
        if combined and combined != ".":
            raw_texts.append(combined)
            metadata.append({
                "title": title,
                "subreddit": subreddit,
                "ups": ups,
                "num_comments": num_comments,
            })

    if not raw_texts:
        print("[WARNING] All posts have empty text. Skipping ML run.")
        return

    # Step 4: Run TrendPipeline with metadata and historical data
    print(f"[INFO] Running TrendPipeline on {len(raw_texts)} texts...")
    pipeline = TrendPipeline()
    results = pipeline.run(raw_texts, metadata=metadata,
                           prev_counts=prev_counts, prev_velocities=prev_velocities)

    print(f"[INFO] TrendPipeline produced {len(results)} topic clusters.")

    # Step 5: Save enriched results back to Postgres
    save_results(engine, results)


if __name__ == "__main__":
    run_ml_pipeline()
