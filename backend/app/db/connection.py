import os
import urllib.parse
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load from .env file at the project root
_ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=True)

DB_USER = os.getenv("DB_USER", "postgres").strip()
DB_PASS = os.getenv("DB_PASSWORD", "").strip()
DB_HOST = os.getenv("DB_HOST", "127.0.0.1").strip()
DB_PORT = os.getenv("DB_PORT", "5433").strip()
DB_NAME = os.getenv("DB_NAME", "reddit_db").strip()

encoded_pass = urllib.parse.quote_plus(DB_PASS)
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)