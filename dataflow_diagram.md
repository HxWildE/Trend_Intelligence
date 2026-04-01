# Trend Intelligence System — Data Flow Diagram

> Traces every data transformation from ingestion to the user's browser. Verified against source code.

---

## Path A — Hourly Batch Pipeline (Time-Triggered)

```mermaid
flowchart TD

%% ── Styles ──────────────────────────────────────────────────────────────────
classDef trigger  fill:#1e1e2e,stroke:#555,color:#fff;
classDef collect  fill:#f59e0b,stroke:#b45309,color:#000;
classDef process  fill:#3b82f6,stroke:#1d4ed8,color:#fff;
classDef store    fill:#ef4444,stroke:#7f1d1d,color:#fff;
classDef ml       fill:#8b5cf6,stroke:#4c1d95,color:#fff;
classDef output   fill:#10b981,stroke:#065f46,color:#fff;
classDef file     fill:#334155,stroke:#475569,color:#fff;

%% ── TRIGGER ─────────────────────────────────────────────────────────────────
CRON["⏰ cron_jobs.py\nPython schedule — fires every 1 hour\nRuns once immediately on startup"]:::trigger

%% ── STEP 1: COLLECT ─────────────────────────────────────────────────────────
CRON -->|"subprocess.run()"| COL

COL["🕷️ reddit_collector.py\n① Iterates 25 subreddits\n② Fetches top 50 posts + 5 comments each\n③ Filters megathreads / daily-discussions\n④ Extracts: post_id, title, text, score,\n   comments, subreddit, created_utc"]:::collect

COL -->|"Fetches raw posts"| REDDIT_API["🌍 Reddit JSON API\n(direct HTTPS, no auth)"]:::collect
REDDIT_API -->|"JSON response"| COL

COL -->|"pd.DataFrame.to_csv()"| RAW_CSV["📄 collectors/reddit_data.csv\nColumns: post_id · title · text ·\nscore · comments · subreddit · datetime_utc\n~2500 rows per run"]:::file

%% ── STEP 2: CLEAN ───────────────────────────────────────────────────────────
CRON -->|"subprocess.run() — only if Step 1 ✅"| CLEAN

RAW_CSV -->|"pd.read_csv()"| CLEAN

CLEAN["🧹 raw_to_clean.py\n① Strip URLs (regex)\n② Remove emojis, special chars\n③ Normalise whitespace & casing\n④ Output: title_clean · text_clean ·\n   comments_clean · score · subreddit · datetime_utc"]:::process

CLEAN -->|"pd.DataFrame.to_csv()"| CLEAN_CSV["📄 collectors/reddit_data_cleaned.csv\nSame schema — human-readable text only"]:::file

%% ── STEP 3: LOAD ────────────────────────────────────────────────────────────
CRON -->|"subprocess.run() — only if Step 2 ✅"| LOADER

CLEAN_CSV -->|"pd.read_csv()"| LOADER

LOADER["📥 db_loader.py  ·  DataLoader.load_to_postgres()\n① Drop intra-batch duplicates (keep last per post_id)\n② Rename cols → schema names\n   title_clean→title · text_clean→content\n   score→ups · datetime_utc→created_utc\n③ Convert created_utc → TIMESTAMP\n④ Compute num_comments from pipe-delimited string\n⑤ Write to temp table\n⑥ UPSERT: ON CONFLICT (post_id) DO UPDATE\n   ups, num_comments, content, processed_at"]:::process

LOADER -->|"SQLAlchemy · UPSERT"| PG_RAW[("🐘 PostgreSQL\nreddit_trends\npost_id · title · content · ups\nnum_comments · subreddit\ncreated_utc · processed_at")]:::store

%% ── STEP 4: ML ENGINE ───────────────────────────────────────────────────────
CRON -->|"subprocess.run() — only if Step 3 ✅"| ML_RUNNER

ML_RUNNER["🔗 ml_runner.py  (orchestrator)\n① Reads schema.sql → ensures tables exist\n② AUTO-PURGE: deletes rows > 24 h old\n   from reddit_trends AND ml_trend_results\n③ fetch_latest_posts() — latest 500 rows\n④ fetch_previous_run() — prev topic volumes\n   for velocity / acceleration tracking\n⑤ Builds combined text: title + content\n⑥ Calls TrendPipeline.run()"]:::ml

PG_RAW -->|"SELECT 500 newest rows\n(ORDER BY processed_at DESC)"| ML_RUNNER
PG_OLD[("🐘 PostgreSQL\nml_trend_results\n(previous run)")]:::store
PG_OLD -->|"SELECT topic_id, volume, velocity\nWHERE run_at = MAX(run_at)"| ML_RUNNER

ML_RUNNER --> PIPELINE

subgraph PIPELINE["🧠 TrendPipeline.run()  — ml_engine/pipelines/trend_pipeline.py"]
    direction TB
    P1["① PreprocessingPipeline\nregex clean on each text"]:::ml
    P2["② SentimentInference  (NLTK VADER)\ncompound score −1→+1\nlabel: positive / neutral / negative"]:::ml
    P3["③ EmbeddingModel  (sentence-transformers)\nall-MiniLM-L6-v2\n384-dimensional dense vector per text"]:::ml
    P4["④ ClusterModel  (sklearn AgglomerativeClustering)\ndistance_threshold = 1.25\ngroups semantically similar posts"]:::ml
    P5["⑤ TopicLabeler  (TF-IDF Vectorizer)\nextracts top-5 keywords per cluster"]:::ml
    P6["⑥ Aggregation per cluster\nvolume · avg_sentiment · subreddits\ntop-3 posts by upvotes · avg_ups · avg_comments\nFILTER: discard clusters with < 3 posts"]:::ml
    P7["⑦ VelocityCalculator\ncurrent_volume − previous_volume"]:::ml
    P8["⑧ AccelerationCalculator\ncurrent_velocity − previous_velocity"]:::ml
    P9["⑨ TrendScorer\n0.35×Volume + 0.30×Velocity\n+0.20×Acceleration + 0.15×Sentiment"]:::ml
    P10["⑩ Sort DESC by score · cap to Top 20"]:::ml
    P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> P7 --> P8 --> P9 --> P10
end

PIPELINE -->|"List of enriched cluster dicts"| ML_RUNNER

ML_RUNNER -->|"Bulk INSERT — all clusters share\none run_at = datetime.now(UTC)"| PG_ML[("🐘 PostgreSQL\nml_trend_results\ntopic_id · keywords · score · volume\nvelocity · acceleration · sentiment\nsentiment_label · positive/neg/neu_pct\ntop_posts · subreddits · avg_ups\navg_comments · run_at")]:::store
```

---

## Path B — Live Search (User-Triggered, Real-Time)

```mermaid
flowchart TD

classDef ui       fill:#3b82f6,stroke:#1d4ed8,color:#fff;
classDef gateway  fill:#1e1e2e,stroke:#555,color:#fff;
classDef backend  fill:#10b981,stroke:#065f46,color:#fff;
classDef store    fill:#ef4444,stroke:#7f1d1d,color:#fff;
classDef cache    fill:#f97316,stroke:#c2410c,color:#fff;
classDef worker   fill:#a21caf,stroke:#701a75,color:#fff;
classDef external fill:#6b7280,stroke:#374151,color:#fff;

USER["👤 User types query\nin Search.jsx"]:::ui
USER -->|"POST /api/search?query=X"| GW["🌐 Nginx Gateway :8080"]:::gateway
GW -->|"Proxy → :8000"| API["⚡ FastAPI\nroutes/search.py"]:::backend
API --> SS["search_service.py\nsearch_logic(query)"]:::backend

%% Branch A: ML cache hit
SS -->|"① _lookup_ml_score()\nSELECT ml_trend_results\nWHERE keywords ILIKE '%word%'"| PG_ML[("🐘 PostgreSQL\nml_trend_results")]:::store
PG_ML -->|"score > 0 → use it"| SS

%% Branch B: ML miss → live VADER
SS -->|"② score == 0\nCache miss → live fallback"| VADER["_live_vader_fallback()\nhttpx async GET Reddit /search.json\nlimit=50, sort=new"]:::backend
VADER -->|"HTTPS request"| RDT["🌍 Reddit JSON API"]:::external
RDT -->|"up to 50 posts"| VADER

VADER -->|"< 5 Reddit results?\nNewsAPI fallback"| NEWS_API["🌍 NewsAPI.org\npageSize=100, sortBy=publishedAt"]:::external
NEWS_API -->|"articles JSON"| VADER

VADER -->|"NLTK VADER compound score\n→ fast_score formula"| SS

%% Enqueue worker job
SS -->|"③ LPUSH query → search_queue"| REDIS_Q[("Redis\nList: search_queue")]:::cache

%% Save search record
SS -->|"④ INSERT INTO searches\n(query, trend_score, region='Global')"| PG_SEARCH[("🐘 PostgreSQL\nsearches\nquery · trend_score · region")]:::store

%% Return to user
SS -->|"⑤ Return JSON\n{query, trend_score}"| API
API --> GW --> USER

%% Worker daemon
REDIS_Q -->|"BRPOP (blocking)\npops query string"| WORKER["🤖 worker.py (Custom Daemon)\n① Scrapes Live Reddit Posts\n② Spawns NER & VADER NLP\n③ Embeds & KMeans Clusters posts\n④ TF-IDF extracts Topic Labels"]:::worker
WORKER -->|"INSERT MLTrendResult\nrun_at = now() · ~1-3 rows"| PG_ML
```

---

## Path C — Trend & Region Pages (Read-Only)

```mermaid
flowchart LR

classDef ui      fill:#3b82f6,stroke:#1d4ed8,color:#fff;
classDef backend fill:#10b981,stroke:#065f46,color:#fff;
classDef store   fill:#ef4444,stroke:#7f1d1d,color:#fff;

FE_G["📄 GlobalTrends.jsx"]:::ui
FE_I["📄 IndiaTrends.jsx"]:::ui

FE_G -->|"GET /api/trends?limit=10"| TS["trend_service.py\nget_trends()\n① run_at = latest batch with ≥3 rows\n② SELECT ORDER BY score DESC LIMIT 10"]:::backend
FE_I -->|"GET /api/region?state=Maharashtra"| RS["region_service.py\nget_region_trends(state)\n① run_at = latest batch with ≥3 rows\n② STATE_KEYWORDS map → search terms\n③ ILIKE filter on subreddits column"]:::backend

TS -->|"Query"| PG[("🐘 PostgreSQL\nml_trend_results")]:::store
RS -->|"Query"| PG

PG -->|"Top clusters"| TS
PG -->|"State-matched clusters"| RS

TS -->|"trends[] JSON"| FE_G
RS -->|"trends[] JSON"| FE_I

FE_G -->|"Renders"| C1["TrendCard · Graph\n(Recharts) · NewsFeed"]:::ui
FE_I -->|"Renders"| C2["StateDropdown · TrendCard\nGraph (Recharts)"]:::ui
```
