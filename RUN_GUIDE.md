# Trend Intelligence Pipeline - Getting Started Guide

This document outlines the step-by-step process to spin up the databases via Docker and run the full ETL + ML pipeline end-to-end.

---

## Prerequisites

- **Docker Desktop** installed and running
- **Python 3.10+** with a virtual environment set up in the project root
- A `.env` file at the project root with your database credentials:
  ```env
  DB_USER=postgres
  DB_PASSWORD=123456
  DB_HOST=localhost
  DB_PORT=5432
  DB_NAME=reddit_db
  MONGO_URI=mongodb://localhost:27017/
  ```

---

## Step 1: Spin Up the Databases (Docker)

The project uses **PostgreSQL** (structured analytics) and **MongoDB** (raw document storage).

1. Open a terminal in the project root.
2. Start both databases in the background:
   ```bash
   docker-compose up -d
   ```
3. Verify they are running:
   ```bash
   docker ps
   ```
   You should see `trend_postgres` on port `5432` and `trend_mongo` on port `27017`.

---

## Step 2: Install Dependencies

1. Activate your virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\activate
   ```
2. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 3: Run the Full Pipeline (ETL + ML)

The scheduler script runs the entire pipeline in sequence. Database tables are **auto-created** from `database/postgres/schema.sql` on the first run — no manual SQL setup needed.

```bash
.\venv\Scripts\python.exe data_pipeline\schedulers\cron_jobs.py
```

### What Happens Automatically

| Step | Script | What It Does |
|------|--------|-------------|
| 1. Collect | `reddit_collector.py` | Scrapes Reddit hot posts → `reddit_data.csv` |
| 2. Clean | `raw_to_clean.py` | Removes URLs, emojis, special chars → `reddit_data_cleaned.csv` |
| 3. Load | `db_loader.py` | Upserts cleaned data to Postgres (`reddit_trends`) + MongoDB |
| 4. ML Analysis | `ml_runner.py` | Runs TrendPipeline → saves enriched results to `ml_trend_results` |

The scheduler **repeats every hour** automatically. Press `Ctrl+C` to stop it.

---

## Step 4: Verify Results

### Check Postgres Tables
```bash
docker exec -it trend_postgres psql -U postgres -d reddit_db -c "\dt"
```
You should see both `reddit_trends` and `ml_trend_results`.

### View Raw Posts
```bash
docker exec -it trend_postgres psql -U postgres -d reddit_db -c "SELECT post_id, title, subreddit, ups FROM reddit_trends LIMIT 5;"
```

### View ML Trend Results
```bash
docker exec -it trend_postgres psql -U postgres -d reddit_db -c "SELECT topic_id, keywords, sentiment_label, positive_pct, negative_pct, avg_ups, score FROM ml_trend_results ORDER BY score DESC;"
```

### View Representative Posts & Subreddits
```bash
docker exec -it trend_postgres psql -U postgres -d reddit_db -c "SELECT topic_id, subreddits, LEFT(top_posts, 120) FROM ml_trend_results ORDER BY score DESC;"
```

---

## Running Individual Components

You can also run each step independently:

```bash
# Just the data collector
.\venv\Scripts\python.exe data_pipeline\collectors\reddit_collector.py

# Just the data cleaner
.\venv\Scripts\python.exe data_pipeline\processors\raw_to_clean.py

# Just the DB loader
.\venv\Scripts\python.exe data_pipeline\loaders\db_loader.py

# Just the ML engine
.\venv\Scripts\python.exe ml_engine\pipelines\ml_runner.py
```

---

## ML Trend Results Schema

Each row in `ml_trend_results` represents a **topic cluster**, not individual posts:

| Column | Description |
|--------|-------------|
| `topic_id` | Cluster ID |
| `keywords` | Top 5 meaningful keywords (stopwords filtered) |
| `volume` | Number of posts in this cluster |
| `velocity` | Growth rate vs previous run |
| `acceleration` | Change in growth rate |
| `sentiment` | Average sentiment score (-1 to 1) |
| `sentiment_label` | Majority label: positive / negative / neutral |
| `positive_pct` | % of posts with positive sentiment |
| `negative_pct` | % of posts with negative sentiment |
| `neutral_pct` | % of posts with neutral sentiment |
| `top_posts` | Top 3 post titles by upvotes |
| `subreddits` | List of contributing subreddits |
| `avg_ups` | Average upvotes across cluster |
| `avg_comments` | Average comments across cluster |
| `score` | Overall trend score (higher = more trending) |
| `run_at` | Timestamp of this ML run |
