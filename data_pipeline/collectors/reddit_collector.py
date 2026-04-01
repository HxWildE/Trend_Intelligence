import requests
import pandas as pd
from datetime import datetime
import time
from tqdm import tqdm
import os
import sys

# Add the parent directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Use the strict User-Agent from config
HEADERS = {
    "User-Agent": config.USER_AGENT
}

BATCH_SIZE = 25  # Reduced batch size slightly for better stability
LIMIT_COMMENTS = config.COMMENT_LIMIT

session = requests.Session()
session.headers.update(HEADERS)

def fetch_comments(subreddit, post_id):
    # Added 'depth=1' to avoid loading deep nested replies (saves time)
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json?limit={LIMIT_COMMENTS}&depth=1"
    try:
        # Reduced timeout to 3 seconds. If Reddit doesn't respond, we skip it.
        response = session.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                comment_data = data[1]['data']['children']
                comments = [c['data'].get('body', '') for c in comment_data if c['kind'] == 't1']
                return " | ".join(comments) if comments else "No Comments"
    except:
        return "No Comments (Timeout)"
    return "No Comments"

def fetch_reddit_data(source_type, query, total_needed):
    all_posts = []
    after = None
    
    pbar = tqdm(total=total_needed, desc=f" 🔍 Fetching {query}", leave=True)

    while len(all_posts) < total_needed:
        base_url = f"https://www.reddit.com/r/{query}/hot.json" if source_type == "subreddit" else "https://www.reddit.com/search.json"
        params = {
            "limit": BATCH_SIZE,
            "q": query if source_type == "keyword" else None,
            "after": after
        }

        try:
            # Increased timeout for the main post list
            response = session.get(base_url, params=params, timeout=10)
            
            if response.status_code == 429:
                # Sleep heavily to clear the API rate-limit bucket, then abandon the current query 
                # to prevent infinite loop deadlocks. (We keep whatever posts we already grabbed!)
                print(f"\n[WARNING] Reddit Rate Limit (429) hit on {query}. Sleeping 60s then skipping to next topic...")
                time.sleep(60)
                break
                
            if response.status_code != 200:
                break

            data = response.json().get('data', {})
            children = data.get('children', [])
            if not children:
                break

            for post in children:
                p = post['data']
                title = p.get("title", "").lower()
                
                # Skip meta/daily-discussion threads that pollute NLP clustering
                if any(noise in title for noise in ["megathread", "discussion thread", "daily thread", "weekly thread"]):
                    continue
                
                # Fetch comments
                comments = fetch_comments(p.get("subreddit"), p.get("id"))

                all_posts.append({
                    "post_id": p.get("id"),  # Retained the post_id mapping to allow upserts!
                    "title": p.get("title"),
                    "text": p.get("selftext", "No Text"),
                    "comments": comments,
                    "score": p.get("score"),
                    "subreddit": p.get("subreddit"),
                    "datetime_utc": datetime.fromtimestamp(p.get("created_utc", 0))
                })
                
                pbar.update(1)
                if len(all_posts) >= total_needed:
                    break

            after = data.get('after')
            if not after:
                break
            
            # Small delay to be polite to the server
            time.sleep(1)

        except Exception as e:
            print(f" Error on {query}: {e}")
            break

    pbar.close()
    return all_posts

from sqlalchemy import create_engine, text

def build_dataset():
    # Utilizing configuration settings instead of hardcoding
    subreddits = config.SUBREDDITS
    keywords = config.KEYWORDS
    
    # 🌟 NEW ARCHITECTURE: Fetch dynamic user searches from the database!
    try:
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT query FROM searches ORDER BY id DESC LIMIT 15"))
            db_keywords = [row[0] for row in result.fetchall()]
            if db_keywords:
                print(f"[INFO] Found {len(db_keywords)} custom user searches in database! Adding to scrape queue...")
                keywords = list(set(keywords + db_keywords))
    except Exception as e:
        print(f"[WARNING] Could not connect to DB for custom keywords. Using defaults. ({e})")

    # Pulling directly from config to dynamically allow 50+ posts per topic!
    total_needed = config.POST_LIMIT 
    
    final_list = []
    
    print("[INFO] Starting Data Collection via manual HTTP JSON requests...")
    for sub in subreddits:
        final_list.extend(fetch_reddit_data("subreddit", sub, total_needed))
    for key in keywords:
        final_list.extend(fetch_reddit_data("keyword", key, total_needed))
        
    if final_list:
        df = pd.DataFrame(final_list)
        # Using central config file path
        save_path = config.RAW_DATA_PATH
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"\n[SUCCESS] Done! Saved {len(df)} rows to {save_path}")
    else:
        print("\n[ERROR] No data collected. Check your internet, Reddit status, or rate limits.")

if __name__ == "__main__":
    build_dataset()