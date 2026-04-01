from sqlalchemy import text
from app.db.connection import SessionLocal
from app.models.search import Search
from app.models.ml_trend_result import MLTrendResult
from app.utils.logger import log
from fastapi import HTTPException
import httpx
from nltk.sentiment import SentimentIntensityAnalyzer


def _lookup_ml_score(db, query: str) -> float:
    """
    Look up a trend score for the query from the latest ML run.

    Searches the `keywords` column of ml_trend_results for any cluster
    whose keywords overlap with words in the query string. Returns the
    highest matching cluster's composite score, or 0.0 if no match.
    """
    try:
        # Protect against lone LIVE_SEARCH entries hijacking MAX(run_at)
        latest_run = db.execute(
            text("""
                SELECT run_at
                FROM ml_trend_results
                WHERE subreddits NOT LIKE '%LIVE_SEARCH%'
                GROUP BY run_at
                HAVING COUNT(*) >= 3
                ORDER BY run_at DESC
                LIMIT 1
            """)
        ).scalar()

        if latest_run is None:
            return 0.0

        # Try each word in the query against the keywords column
        words = [w.strip().lower() for w in query.split() if len(w.strip()) > 2]
        best_score = 0.0

        for word in words:
            match = (
                db.query(MLTrendResult)
                .filter(
                    MLTrendResult.run_at == latest_run,
                    MLTrendResult.keywords.ilike(f"%{word}%")
                )
                .order_by(MLTrendResult.score.desc())
                .first()
            )
            if match and match.score and match.score > best_score:
                best_score = match.score

        return round(best_score, 2)
    except Exception:
        return 0.0

import os
import sys

# Try loading config for API Keys
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from data_pipeline.config import config
    NEWS_API_KEY = config.NEWS_API_KEY
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

async def _live_vader_fallback(query: str) -> float:
    """Fast real-time fetch + sentiment analysis safety net."""
    try:
        url = "https://www.reddit.com/search.json"
        headers = {"User-Agent": "TrendIntelligence/1.0.FastAPI"}
        params = {"q": query, "limit": 50, "sort": "new"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=5.0)
            
        posts = []
        if response.status_code == 200:
            posts = response.json().get("data", {}).get("children", [])
            
        analyzer = SentimentIntensityAnalyzer()
        
        # ⚡ NEW: NewsAPI Fallback if Reddit returns barely any results
        if len(posts) < 5 and NEWS_API_KEY and NEWS_API_KEY != "your_news_api_key_here":
            napi_url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=100&apiKey={NEWS_API_KEY}"
            async with httpx.AsyncClient() as client:
                n_res = await client.get(napi_url, timeout=5.0)
            
            if n_res.status_code == 200:
                n_data = n_res.json()
                total_results = n_data.get("totalResults", 0)
                articles = n_data.get("articles", [])
                
                n_sentiments = []
                for art in articles[:20]: # Analyze top 20
                    text_str = str(art.get("title", "")) + " " + str(art.get("description", ""))
                    if text_str.strip():
                        n_sentiments.append(analyzer.polarity_scores(text_str)["compound"])
                
                n_avg = sum(n_sentiments) / len(n_sentiments) if n_sentiments else 0.0
                n_base_score = min(total_results * 0.8, 75.0) # Boost based on total global coverage
                
                if total_results > 0:
                    fast_score = n_base_score + (n_avg * 25.0)
                    return round(max(0.0, min(99.0, fast_score)), 2)
            
        # Continue with Reddit logic if we have reddit posts
        if not posts:
            return 0.0
            
        sentiments = []
        for post in posts:
            text = post["data"].get("title", "") + " " + post["data"].get("selftext", "")
            if text.strip():
                score = analyzer.polarity_scores(text)["compound"]
                sentiments.append(score)
                
        if not sentiments:
            return 0.0
            
        avg_sentiment = sum(sentiments) / len(sentiments)
        volume = len(posts)
        
        base_volume_score = (volume * 1.5)
        if volume >= 49:
            base_volume_score += 25.0 
            
        fast_score = base_volume_score + (avg_sentiment * 30.0)
        return round(max(0.0, min(99.0, fast_score)), 2)
    except Exception as e:
        print(f"Fallback Error for {query}: {e}")
        return 0.0

async def search_logic(query: str):
    """
    Look up the trend score for the query from ML results and save to the DB.

    The score comes from the most recent ML pipeline run: we search the
    keywords of each topic cluster for words in the user's query and return
    the highest matching cluster score. Falls back to 0 if the ML pipeline
    hasn't produced data yet.
    """
    log(f"Search query received: {query}")

    db = SessionLocal()
    try:
        # --- Real trend score from ML results ---
        trend_score = _lookup_ml_score(db, query)
        
        # ⚡ NEW ARCHITECTURE: Live Async VADER Safety Net
        if trend_score <= 0.0:
            log(f"Cache miss for '{query}'. Triggering fast live VADER fallback...")
            trend_score = await _live_vader_fallback(query)

        new_search = Search(
            query=query,
            trend_score=int(trend_score),
            region="Global",
        )

        db.add(new_search)
        db.commit()

        return {
            "query": query,
            "trend_score": trend_score,
            "message": "saved to DB",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


#ML processing data
def call_ml(query: str):
    # Simulates an ML prediction returning a dummy trend and score
    # Simulated machine learning engine response (placeholder for real ML model)
    return {
        "trend": "dummy trend",
        "score": 0.95  # Mock confidence score
    }

# reads all data from database and returns it as JSON
def get_all_searches():
    # Retrieves all past search queries from the DB
    db = SessionLocal()
    try:
        data = db.query(Search).all()

        result = []
        for item in data:
            result.append({
                "id": item.id,
                "query": item.query,
                "trend_score": item.trend_score
            })
        return result
    finally:
        db.close()


def get_search_by_id(search_id: int):
    # Fetches a specific search record by its DB ID
    db = SessionLocal()
    try:
        data = db.query(Search).filter(Search.id == search_id).first()

        if not data:
            raise HTTPException(status_code=404, detail="Search not found")

        return {
            "id": data.id,
            "query": data.query,
            "trend_score": data.trend_score
        }
    finally:
        db.close()

def delete_search(search_id: int):
    # Removes a specific search record from the DB by ID
    db = SessionLocal()
    try:
        data = db.query(Search).filter(Search.id == search_id).first()

        if not data:
            raise HTTPException(status_code=404, detail="Search not found")

        db.delete(data)
        db.commit()

        return {"message": "deleted"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()