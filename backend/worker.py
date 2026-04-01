import os
import sys
import datetime
import redis
import time
import httpx

# Fix path to load module correctly when run from backend root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db.connection import SessionLocal
from backend.app.models.ml_trend_result import MLTrendResult

# NEW: Import the real ML pipeline
from ml_engine.pipelines.trend_pipeline import TrendPipeline

def fetch_live_reddit_posts(query: str, limit: int = 100):
    url = "https://www.reddit.com/search.json"
    headers = {"User-Agent": "TrendIntelligence/1.0.Worker"}
    params = {"q": query, "limit": limit, "sort": "new"}
    
    try:
        response = httpx.get(url, headers=headers, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("children", [])
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ Reddit Fetch Error: {e}")
        return []

def run_search_ml_pipeline(query: str):
    """
    Background worker job executed via RQ (Redis Queue).
    Now performs REAL deep Machine Learning on live searches.
    """
    print(f"[{datetime.datetime.now()}] 🛠️ WORKER STARTED deep ML Pipeline for query: {query}")
    
    # 1. Scrape Reddit synchronously
    print(f"[{datetime.datetime.now()}] 🕷️ Scraper Component: Harvesting {query} from Reddit...")
    posts = fetch_live_reddit_posts(query)
    
    if not posts:
        print(f"[{datetime.datetime.now()}] ❌ No posts found for '{query}'. Aborting ML.")
        return

    raw_texts = []
    metadata = []
    
    for post in posts:
        post_data = post.get("data", {})
        title = post_data.get("title", "")
        content = post_data.get("selftext", "")
        ups = post_data.get("ups", 0)
        num_comments = post_data.get("num_comments", 0)
        
        combined = f"{title}. {content}".strip()
        if combined and combined != ".":
            raw_texts.append(combined)
            metadata.append({
                "title": title,
                "subreddit": "LIVE_SEARCH",  # ⚡ THIS IS CRITICAL TO PREVENT DASHBOARD HIJACKING
                "ups": ups,
                "num_comments": num_comments,
            })
            
    print(f"[{datetime.datetime.now()}] 🧠 ML Component: Running TrendPipeline on {len(raw_texts)} real texts (NER, VADER, MiniLM, KMeans)...")
    
    # Run the actual pipeline!
    pipeline = TrendPipeline()
    results = pipeline.run(raw_texts, metadata=metadata)
    
    if not results:
        print(f"[{datetime.datetime.now()}] ⚠️ ML Component: No significant clusters formed for '{query}'.")
        return
        
    print(f"[{datetime.datetime.now()}] 📊 ML Component: Produced {len(results)} deep clusters for '{query}'!")

    # 4. Save Final ML Data to PostgreSQL Database
    db = SessionLocal()
    try:
        run_timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        for res in results:
            new_ml_trend = MLTrendResult(
                run_at=run_timestamp,
                topic_id=int(res["topic_id"]),
                volume=int(res.get("volume", 0)),
                velocity=float(res.get("velocity", 0.0)),
                acceleration=float(res.get("acceleration", 0.0)),
                sentiment=float(res.get("sentiment", 0.0)),
                sentiment_label=str(res.get("sentiment_label", "neutral")),
                positive_pct=float(res.get("positive_pct", 0)),
                negative_pct=float(res.get("negative_pct", 0)),
                neutral_pct=float(res.get("neutral_pct", 0)),
                top_posts=str(res.get("top_posts", "")),
                subreddits=str(res.get("subreddits", "LIVE_SEARCH")),
                avg_ups=float(res.get("avg_ups", 0)),
                avg_comments=float(res.get("avg_comments", 0)),
                keywords=str(", ".join(res.get("keywords", []))),
                score=float(res.get("score", 0.0))
            )
            db.add(new_ml_trend)
            
        db.commit()
        print(f"[{datetime.datetime.now()}] ✅ Worker Finished. {len(results)} ML Clusters persisted to PostgreSQL!")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ Worker Database Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    import time
    # Initialise standard Redis connection map
    redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    print("=================================================")
    print("🔥 Windows-Compatible Redis Worker Daemon Initialised 🔥")
    print("Connected to Redis (localhost:6379)")
    print("Listening for jobs on native queue: 'search_queue'")
    print("=================================================")
    
    while True:
        try:
            # Block until a job is pushed to the queue
            result = redis_conn.brpop("search_queue", timeout=0)
            if result:
                _, query = result
                run_search_ml_pipeline(query)
        except Exception as e:
            print(f"[{datetime.datetime.now()}] ❌ Worker Loop Error: {e}")
            time.sleep(5)

