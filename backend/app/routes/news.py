from fastapi import APIRouter
import requests
from app.services.nlp_summarizer import summarize_text
from datetime import datetime
import os 
import sys

# Hack to load config safely within the backend fast path
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from data_pipeline.config import config
    NEWS_API_KEY = config.NEWS_API_KEY
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

router = APIRouter()

@router.get("/news/realtime")
def get_realtime_news(region: str = None, topic: str = None):
    """
    Fetches the top latest news from HackerNews and NewsAPI, 
    summarizes them, and returns a unified json feed.
    If 'topic' is provided, fetches matching news globally.
    If 'region' is provided (e.g. 'Maharashtra'), ignores HackerNews 
    and selectively searches NewsAPI for local regional breaking news.
    """
    news_feed = []

    # 1. Hacker News Fetch (Only if NO state or topic is physically selected)
    if not region and not topic:
        try:
            hn_res = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=5)
            if hn_res.status_code == 200:
                top_hn_ids = hn_res.json()[:6]  # Limit to 6 for speed
                
                for sid in top_hn_ids:
                    item_res = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=3)
                    if item_res.status_code == 200:
                        item = item_res.json()
                        if item and item.get("type") == "story":
                            raw_text = item.get("text") or item.get("title", "")
                            news_feed.append({
                                "id": f"hn_{sid}",
                                "source": "Hacker News",
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "summary": summarize_text(raw_text),
                                "timestamp": datetime.fromtimestamp(item.get("time", 0)).isoformat()
                            })
        except Exception as e:
            print(f"[ERROR] HackerNews fetch failed: {e}")

    # 2. News API Fetch
    if NEWS_API_KEY and NEWS_API_KEY != "your_news_api_key_here":
        try:
            # Dynamically switch between General Headlines, Topic, or Local Breaking queries
            if topic:
                url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=publishedAt&pageSize=6&apiKey={NEWS_API_KEY}"
            elif region and region.lower() != "india":
                url = f"https://newsapi.org/v2/everything?q={region}&language=en&sortBy=publishedAt&pageSize=6&apiKey={NEWS_API_KEY}"
            else:
                url = f"https://newsapi.org/v2/top-headlines?country=in&language=en&pageSize=6&apiKey={NEWS_API_KEY}"
                
            napi_res = requests.get(url, timeout=5)
            if napi_res.status_code == 200:
                articles = napi_res.json().get("articles", [])
                
                for i, art in enumerate(articles):
                    raw_text = str(art.get("description") or "") + " " + str(art.get("content") or "")
                    news_feed.append({
                        "id": f"napi_{i}",
                        "source": art.get("source", {}).get("name", "NewsAPI"),
                        "title": art.get("title", ""),
                        "url": art.get("url", ""),
                        "summary": summarize_text(raw_text) if raw_text.strip() else "",
                        "timestamp": art.get("publishedAt", "")
                    })
        except Exception as e:
            print(f"[ERROR] NewsAPI fetch failed: {e}")

    # Sort descending by timestamp (newest first)
    def parse_time(t):
        try:
            if not t: return 0
            t_str = str(t).replace('Z', '+00:00')
            return datetime.fromisoformat(t_str).timestamp()
        except Exception:
            return 0

    news_feed.sort(key=lambda x: parse_time(x.get("timestamp", "")), reverse=True)
    return news_feed
