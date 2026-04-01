import sys
import os
import requests
import pandas as pd
from datetime import datetime

# Add the parent directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Import DataLoader to write directly to Postgres
loader_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'loaders')
sys.path.append(loader_path)
try:
    from db_loader import DataLoader
except ImportError:
    print("[ERROR] Could not import DataLoader")
    DataLoader = None

def fetch_global_news(limit=50):
    api_key = config.NEWS_API_KEY
    if not api_key or api_key == "your_news_api_key_here":
        print("[WARNING] NEWS_API_KEY is missing. Skipping News API.")
        return []
        
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize={limit}&apiKey={api_key}"
    posts = []
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            print(f"[INFO] Fetching {len(articles)} articles from News API...")
            
            for index, item in enumerate(articles):
                if item and item.get("title") and item.get("url"):
                    
                    # Construct text from description and content
                    content = []
                    if item.get("description"):
                        content.append(item.get("description"))
                    if item.get("content"):
                        content.append(item.get("content"))
                        
                    content.append(f"Link: {item.get('url')}")
                    
                    source_name = item.get("source", {}).get("name", "NewsAPI")
                    published_at = item.get("publishedAt", "")
                    
                    try:
                        dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                    except:
                        dt = datetime.now()

                    posts.append({
                        "post_id": f"newsapi_{index}_{dt.strftime('%d%H%M')}",
                        "title": item.get("title", ""),
                        "content": " | ".join(content),
                        "ups": 0, # NewsAPI doesn't return upvotes
                        "num_comments": 0,
                        "subreddit": source_name,
                        "created_utc": dt
                    })
        else:
            print(f"[ERROR] NewsAPI returned {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to fetch NewsAPI: {e}")
        
    return posts

if __name__ == "__main__":
    print("[INFO] Starting News API Collector...")
    data = fetch_global_news(config.POST_LIMIT)
    
    if data:
        df = pd.DataFrame(data)
        print(f"[SUCCESS] Fetched {len(df)} News API posts.")
        # Load directly to DB
        if DataLoader:
            loader = DataLoader()
            # We map NewsAPI to reddit_trends so ML Engine easily picks it up
            loader.load_to_postgres(df, "reddit_trends")
    else:
        print("[WARNING] No data collected from News API.")
