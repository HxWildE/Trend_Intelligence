import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly find the .env at the project root (works regardless of cwd)
# override=True ensures .env values win over any stale shell env vars
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=True)

class Config:
    # 📂 1. Directory Paths
    # This automatically finds the root of your project
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = os.path.join(BASE_DIR, "data_pipeline", "collectors")
    
    RAW_DATA_PATH = os.path.join(DATA_DIR, "reddit_data.csv")
    CLEAN_DATA_PATH = os.path.join(DATA_DIR, "reddit_data_cleaned.csv")

    # 🌐 2. Reddit Scraping Settings
    SUBREDDITS = ["technology", "news", "science", "business", "worldnews"]
    KEYWORDS = ["AI", "Nvidia", "GPT", "crypto", "startup"]
    
    POST_LIMIT = 50       # Number of posts per category
    COMMENT_LIMIT = 5     # Number of comments per post
    USER_AGENT = "pc:trend_intelligence:v1.0 (by /u/abdullah_khan_nitw)"
    
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")

    # 🗄️ 3. Database Configurations
    # Postgres (SQL)
    DB_USER = os.getenv("DB_USER", "postgres").strip()
    DB_PASS = os.getenv("DB_PASSWORD", "").strip()
    DB_HOST = os.getenv("DB_HOST", "localhost").strip()
    DB_PORT = os.getenv("DB_PORT", "5432").strip()
    DB_NAME = os.getenv("DB_NAME", "reddit_db").strip()
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # MongoDB (NoSQL)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = "trend_intelligence_db"

    # 🕒 4. Scheduler Settings
    RUN_EVERY_HOURS = 1

# Instantiate the config to be used across the app
config = Config()