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

def fetch_hacker_news(limit=50):
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    posts = []
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            story_ids = response.json()[:limit]
            print(f"[INFO] Fetching {len(story_ids)} stories from Hacker News...")
            
            for sid in story_ids:
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                try:
                    item_res = requests.get(item_url, timeout=5)
                    if item_res.status_code == 200:
                        item = item_res.json()
                        if item and item.get("type") == "story" and not item.get("deleted"):
                            content = []
                            if item.get("text"):
                                content.append(item.get("text"))
                            if item.get("url"):
                                content.append(f"Link: {item.get('url')}")
                                
                            posts.append({
                                "post_id": f"hn_{sid}",
                                "title": item.get("title", ""),
                                "content": " | ".join(content),
                                "ups": item.get("score", 0),
                                "num_comments": item.get("descendants", 0),
                                "subreddit": "HackerNews",
                                "created_utc": datetime.fromtimestamp(item.get("time", 0))
                            })
                except Exception as e:
                    pass
    except Exception as e:
        print(f"[ERROR] Failed to fetch HackerNews: {e}")
        
    return posts

if __name__ == "__main__":
    print("[INFO] Starting Hacker News Collector...")
    data = fetch_hacker_news(config.POST_LIMIT)
    
    if data:
        df = pd.DataFrame(data)
        print(f"[SUCCESS] Fetched {len(df)} HackerNews posts.")
        # Load directly to DB
        if DataLoader:
            loader = DataLoader()
            # We map HN to reddit_trends so ML Engine easily picks it up
            loader.load_to_postgres(df, "reddit_trends")
    else:
        print("[WARNING] No data collected from Hacker News.")
