# Trend Intelligence ETL Pipeline - Getting Started Guide

This document outlines the step-by-step process required to spin up the local databases via Docker and run the Python data pipeline end-to-end.

---

## Step 1: Spin up the Databases (Docker)

The project relies on Docker to host **PostgreSQL** (structured analytics) and **MongoDB** (raw document storage).

1. Open a terminal in the root of your project (`Trend_Intelligence`).
2. Run the following command to start both databases in the background:
   ```bash
   docker-compose up -d
   ```
3. To verify they are running, type:
   ```bash
   docker ps
   ```
   *You should see `trend_postgres` running on port `5432` and `trend_mongo` running on port `27017`.*

---

## Step 2: Initialize the PostgreSQL Database Schema

Because we updated the pipeline to intelligently prevent duplicating data during the load phase, the PostgreSQL database requires a strict format including a unique `post_id`.

If this is your first time setting it up, or if your pipeline is throwing database relation errors, you must initialize the schema:

1. Copy the code inside `database/postgres/schema.sql`. Make sure it looks like this:
   ```sql
   CREATE TABLE IF NOT EXISTS reddit_trends (
       id SERIAL PRIMARY KEY,
       post_id VARCHAR(50) UNIQUE,
       title TEXT NOT NULL,
       content TEXT,
       ups INTEGER,
       num_comments INTEGER,
       subreddit VARCHAR(100),
       created_utc TIMESTAMP,
       sentiment_score FLOAT DEFAULT 0.0,
       processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```
2. You can execute this against your Docker Postgres database either via:
   - A visual tool like **pgAdmin**, **DBeaver**, or **DataGrip** (connect using `localhost`, port `5432`, user `postgres`, pass `123456`).
   - Or quickly using Docker via the command line:
     ```bash
     docker exec -it trend_postgres psql -U postgres -d reddit_db -f /path/to/schema.sql
     # Or alternatively paste the SQL block directly into the interactive prompt:
     docker exec -it trend_postgres psql -U postgres -d reddit_db
     ```

---

## Step 3: Run the Python Pipeline!

With the databases running and the Postgres schema locked in, you're ready to execute the pipeline scraper. 

1. Ensure your Python virtual environment is activated:
   ```bash
   # On Windows:
   .venv\Scripts\activate
   ```
2. Install dependencies (if you haven't already):
   ```bash
   pip install -r requirements.txt
   ```
3. Run the automated master scheduler script! (Using the direct `.venv` executor path prevents Windows from launching your globally installed Python by mistake):
   ```bash
   .\.venv\Scripts\python.exe data_pipeline\schedulers\cron_jobs.py
   ```

### Expected Output Process
When you run the script, it will automatically:
1. **Collector (`reddit_collector.py`)**: Use HTTP requests to securely pull Reddit hot posts and scrape out mapping fields like the `post_id`, saving it to `reddit_data.csv`.
2. **Processor (`raw_to_clean.py`)**: Scrub emojis, URLs, and weird characters out of the text and comments, saving it to `reddit_data_cleaned.csv`.
3. **Loader (`db_loader.py`)**: Insert the raw dictionaries directly into MongoDB, and cleanly Upsert (Insert or Update if duplicate) the cleaned DataFrames into your Postgres `reddit_trends` table!

If left open, the scheduler will wait and re-run this entire pipeline sequence every hour. Press `CTRL+C` in your terminal to stop it.
