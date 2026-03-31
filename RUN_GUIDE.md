# Trend Intelligence System — Complete Run Guide

This guide walks you through every step to get the **entire system running** from scratch:
databases → data pipeline → ML engine → backend API → frontend.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Project Structure at a Glance](#2-project-structure-at-a-glance)
3. [Environment Setup (.env)](#3-environment-setup-env)
4. [Step 1 — Start the Databases (Docker)](#4-step-1--start-the-databases-docker)
5. [Step 2 — Set Up the Python Virtual Environment](#5-step-2--set-up-the-python-virtual-environment)
6. [Step 3 — Run the Data Pipeline (ETL)](#6-step-3--run-the-data-pipeline-etl)
7. [Step 4 — Run the ML Engine](#7-step-4--run-the-ml-engine)
8. [Step 5 — Start the Backend API](#8-step-5--start-the-backend-api)
9. [Step 6 — Start the Frontend](#9-step-6--start-the-frontend)
10. [Verify Everything is Working](#10-verify-everything-is-working)
11. [Running Everything Together (Quick Reference)](#11-running-everything-together-quick-reference)
12. [Running Individual Components](#12-running-individual-components)
13. [Stopping the System](#13-stopping-the-system)
14. [ML Trend Results Schema](#14-ml-trend-results-schema)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. Prerequisites

Make sure the following are installed before you begin:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| **Docker Desktop** | Latest | `docker --version` |
| **Python** | 3.10+ | `python --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Git** | Any | `git --version` |

> **Windows users:** All commands in this guide assume **PowerShell** or **Command Prompt** run from the project root (`trend-intelligence-system/`).

---

## 2. Project Structure at a Glance

```
trend-intelligence-system/
├── backend/              ← FastAPI REST API
│   ├── app/
│   │   ├── main.py       ← API entry point (run this with uvicorn)
│   │   ├── routes/       ← Endpoint definitions
│   │   ├── services/     ← Business logic (wired to ML results)
│   │   ├── models/       ← SQLAlchemy ORM models
│   │   └── db/           ← Database connection
│   └── requirements.txt
├── frontend/             ← React + Vite app
│   ├── src/
│   └── package.json
├── data_pipeline/        ← ETL: Reddit scraper + cleaner + DB loader
│   ├── collectors/       ← reddit_collector.py
│   ├── processors/       ← raw_to_clean.py
│   ├── loaders/          ← db_loader.py
│   └── schedulers/       ← cron_jobs.py (runs everything hourly)
├── ml_engine/            ← ML: embeddings → clustering → scoring
│   └── pipelines/        ← ml_runner.py (full ML pipeline)
├── docker-compose.yml    ← PostgreSQL + MongoDB containers
├── .env                  ← Your local credentials (create this)
└── req-dev.txt           ← ML/pipeline Python dependencies
```

---

## 3. Environment Setup (.env)

Create a `.env` file in the **project root** (same level as `docker-compose.yml`). This file is read by both the data pipeline and ML engine.

```env
# PostgreSQL (must match docker-compose.yml)
DB_USER=postgres
DB_PASSWORD=123456
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reddit_db

# MongoDB
MONGO_URI=mongodb://localhost:27017/

# Reddit API credentials (required for the data collector)
# Get these from: https://www.reddit.com/prefs/apps → "create another app" → script
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

> **Reddit API setup:**
> 1. Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
> 2. Click **"create another app"**
> 3. Select type: **script**
> 4. Set redirect URI to `http://localhost:8080`
> 5. Copy the **client ID** (under the app name) and **client secret**

> **Note:** The backend uses a hardcoded connection string in `backend/app/db/connection.py`. If your Postgres password is different, update it there too:
> ```
> postgresql://postgres:YourPassword@localhost:5432/trends_db
> ```

---

## 4. Step 1 — Start the Databases (Docker)

The project uses two databases managed by Docker:
- 🐘 **PostgreSQL** (`trend_postgres`) — stores structured post data and ML results
- 🍃 **MongoDB** (`trend_mongo`) — stores raw post documents

### Start containers

Open a terminal in the project root and run:

```bash
docker-compose up -d
```

The `-d` flag runs them in the background.

### Verify they are running

```bash
docker ps
```

Expected output:

```
CONTAINER ID   IMAGE         COMMAND                  PORTS                    NAMES
xxxxxxxxxxxx   postgres:15   "docker-entrypoint.s…"   0.0.0.0:5432->5432/tcp   trend_postgres
xxxxxxxxxxxx   mongo:latest  "docker-entrypoint.s…"   0.0.0.0:27017->27017/tcp trend_mongo
```

### Check database tables (after first pipeline run)

```bash
# List all tables
docker exec -it trend_postgres psql -U postgres -d reddit_db -c "\dt"
```

You should see `reddit_trends` and `ml_trend_results` after the pipeline runs.

---

## 5. Step 2 — Set Up the Python Virtual Environment

All Python components (data pipeline, ML engine, and backend) share the virtual environment at the project root.

### Create and activate the virtual environment

```bash
# Create (only needed once)
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\activate

# Activate (Windows Command Prompt)
.\venv\Scripts\activate.bat
```

Your prompt should now show `(venv)` at the start.

### Install all Python dependencies

There are **two** requirements files — install both:

```bash
# Core backend + pipeline dependencies
pip install -r backend/requirements.txt

# ML engine dependencies (scikit-learn, sentence-transformers, etc.)
pip install -r req-dev.txt

# Data pipeline additional dependency
pip install praw
```

> `praw` is the Reddit Python API wrapper used by the collector. It is not listed in the requirements files, so install it separately.

---

## 6. Step 3 — Run the Data Pipeline (ETL)

The pipeline collects Reddit posts, cleans them, and loads them into Postgres and MongoDB.

### Option A — Run the full automated scheduler (recommended)

This runs all 4 pipeline steps in sequence, then **repeats every hour** automatically:

```bash
.\venv\Scripts\python.exe data_pipeline\schedulers\cron_jobs.py
```

Press `Ctrl+C` to stop the scheduler.

### Option B — Run each step manually

```bash
# Step 1: Collect posts from Reddit → saves to reddit_data.csv
.\venv\Scripts\python.exe data_pipeline\collectors\reddit_collector.py

# Step 2: Clean the raw CSV (strip URLs, emojis, special chars)
.\venv\Scripts\python.exe data_pipeline\processors\raw_to_clean.py

# Step 3: Load cleaned data into Postgres (reddit_trends) and MongoDB
.\venv\Scripts\python.exe data_pipeline\loaders\db_loader.py
```

### What the pipeline does

| Step | Script | Input | Output |
|------|--------|-------|--------|
| Collect | `reddit_collector.py` | Reddit API | `reddit_data.csv` |
| Clean | `raw_to_clean.py` | `reddit_data.csv` | `reddit_data_cleaned.csv` |
| Load | `db_loader.py` | `reddit_data_cleaned.csv` | Postgres `reddit_trends` + MongoDB |

### Verify posts were loaded

```bash
docker exec -it trend_postgres psql -U postgres -d reddit_db -c "SELECT post_id, title, subreddit, ups FROM reddit_trends LIMIT 5;"
```

---

## 7. Step 4 — Run the ML Engine

The ML engine reads posts from Postgres, clusters them into topics, scores trends, and saves results.

```bash
.\venv\Scripts\python.exe ml_engine\pipelines\ml_runner.py
```

> This step is also included in the full scheduler (`cron_jobs.py`). Run it standalone when you want to test ML results without re-fetching data.

### What the ML engine does

| Stage | What Happens |
|-------|-------------|
| Embeddings | Converts post text → 384-dimensional vectors |
| Clustering | Groups similar posts into topic clusters |
| Labeling | Extracts top keywords per cluster (TF-IDF) |
| Sentiment | Scores each cluster positive / negative / neutral |
| Scoring | Computes `score = 0.35×Volume + 0.30×Velocity + 0.20×Acceleration + 0.15×Sentiment` |
| Save | Writes enriched results to `ml_trend_results` table |

### Verify ML results were saved

```bash
# View top trending topics
docker exec -it trend_postgres psql -U postgres -d reddit_db -c "SELECT topic_id, keywords, sentiment_label, score FROM ml_trend_results ORDER BY score DESC;"

# View top posts and subreddits per topic
docker exec -it trend_postgres psql -U postgres -d reddit_db -c "SELECT topic_id, subreddits, LEFT(top_posts, 120) FROM ml_trend_results ORDER BY score DESC;"
```

---

## 8. Step 5 — Start the Backend API

The FastAPI backend serves ML results to the frontend via REST endpoints.

Open a **new terminal**, activate the virtual environment, then run:

```bash
# Activate venv
.\venv\Scripts\activate

# Start the API server from the project root
.\venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

The `--reload` flag auto-restarts the server when you edit code.

### Verify the API is running

Open your browser or use curl:

```
http://127.0.0.1:8000/         → {"status": "API running"}
http://127.0.0.1:8000/trends   → top trending topics from ML results
http://127.0.0.1:8000/docs     → interactive Swagger UI
```

### Available endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Health status |
| `GET` | `/search?q=<term>` | Search a term, get ML trend score |
| `GET` | `/all-searches` | History of all past searches |
| `GET` | `/search/id/<id>` | Get a specific search by ID |
| `DELETE` | `/search/id/<id>` | Delete a search record |
| `GET` | `/trends` | Global top trending topics |
| `GET` | `/region?state=<name>` | State-level trends (e.g. `?state=Maharashtra`) |

---

## 9. Step 6 — Start the Frontend

Open a **new terminal** and navigate into the frontend directory:

```bash
cd frontend
```

### Install Node dependencies (first time only)

```bash
npm install
```

### Start the development server

```bash
npm run dev
```

The app will be available at:

```
http://localhost:5173
```

### Frontend pages

| Page | URL | Description |
|------|-----|-------------|
| Search | `http://localhost:5173/` | Search for a topic and see its trend score |
| Global Trends | `http://localhost:5173/trends` | Top trending topics from the ML engine |
| India Trends | `http://localhost:5173/region` | State-level trends for India |

---

## 10. Verify Everything is Working

Run through this checklist to confirm all layers are connected:

```
✅  docker ps          → trend_postgres and trend_mongo are running
✅  /                  → API returns {"status": "API running"}
✅  /trends            → returns a list of ML topic clusters (not empty)
✅  /region?state=delhi → returns region-filtered trends
✅  localhost:5173     → React app loads with navbar and pages
✅  Search page        → typing a query returns a trend score > 0
```

> If `/trends` returns `{"trends": [], "message": "No ML results yet..."}`, the ML engine hasn't run yet. Go back to [Step 4](#7-step-4--run-the-ml-engine).

---

## 11. Running Everything Together (Quick Reference)

You need **4 separate terminals** running simultaneously for the full system:

```
Terminal 1 (databases — keep running)
──────────────────────────────────────
docker-compose up

Terminal 2 (data pipeline — runs & repeats hourly)
──────────────────────────────────────
.\venv\Scripts\activate
.\venv\Scripts\python.exe data_pipeline\schedulers\cron_jobs.py

Terminal 3 (backend API — keep running)
──────────────────────────────────────
.\venv\Scripts\activate
.\venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000

Terminal 4 (frontend — keep running)
──────────────────────────────────────
cd frontend
npm run dev
```

After Terminal 2 completes its first full run, the frontend will display live trend data.

---

## 12. Running Individual Components

```bash
# Data collection only
.\venv\Scripts\python.exe data_pipeline\collectors\reddit_collector.py

# Data cleaning only
.\venv\Scripts\python.exe data_pipeline\processors\raw_to_clean.py

# DB loading only
.\venv\Scripts\python.exe data_pipeline\loaders\db_loader.py

# ML engine only
.\venv\Scripts\python.exe ml_engine\pipelines\ml_runner.py
```

---

## 13. Stopping the System

```bash
# Stop the frontend and backend
# Press Ctrl+C in each terminal

# Stop and remove Docker containers
docker-compose down

# Stop containers but keep data volumes (safe option)
docker-compose stop
```

> Use `docker-compose down -v` only if you want to **wipe all database data** and start fresh.

---

## 14. ML Trend Results Schema

Each row in `ml_trend_results` represents a **topic cluster** (not an individual post):

| Column | Type | Description |
|--------|------|-------------|
| `topic_id` | int | Cluster ID assigned by ML engine |
| `keywords` | text | Top 5 meaningful keywords (stopwords filtered) |
| `volume` | int | Number of posts in this cluster |
| `velocity` | float | Growth rate vs the previous run |
| `acceleration` | float | Change in growth rate |
| `sentiment` | float | Average sentiment score (−1 to +1) |
| `sentiment_label` | text | `positive` / `negative` / `neutral` |
| `positive_pct` | float | % of posts with positive sentiment |
| `negative_pct` | float | % of posts with negative sentiment |
| `neutral_pct` | float | % of posts with neutral sentiment |
| `top_posts` | text | Top 3 post titles by upvotes |
| `subreddits` | text | Contributing subreddit names |
| `avg_ups` | float | Average upvotes across cluster |
| `avg_comments` | float | Average comments across cluster |
| `score` | float | Composite trend score (higher = more trending) |
| `run_at` | timestamp | When this ML batch was computed |

---

## 15. Troubleshooting

### `connection refused` on port 5432 or 27017
Docker containers aren't running. Run `docker-compose up -d` and wait 5–10 seconds.

### `ModuleNotFoundError` when running Python scripts
The virtual environment isn't active or a dependency is missing.
```bash
.\venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r req-dev.txt
pip install praw
```

### Backend returns `{"trends": [], "message": "No ML results yet..."}`
The ML pipeline hasn't run yet. Run:
```bash
.\venv\Scripts\python.exe ml_engine\pipelines\ml_runner.py
```

### Frontend shows no data / network error in browser console
1. Confirm the backend is running at `http://127.0.0.1:8000`
2. CORS is now configured for `localhost:5173` — make sure the frontend is running on that exact port
3. Check the backend terminal for any error output

### `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` missing
The `.env` file is missing or keys are empty. See [Section 3](#3-environment-setup-env) for setup instructions.

### `password authentication failed for user "postgres"`
The backend `connection.py` has a hardcoded password (`Hima@1234`). Either set your Postgres password to match, or update the `DATABASE_URL` in `backend/app/db/connection.py`.

### Docker port already in use (`5432` or `27017`)
Another instance of Postgres or MongoDB is running locally. Stop the local service or change the host port in `docker-compose.yml`.
