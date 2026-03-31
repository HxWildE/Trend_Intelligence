# Changelog — Critical Bug Fixes

**Date:** 2026-03-30  
**Author:** Antigravity (AI Assistant)  
**Scope:** Backend API — Critical integration fixes

---

## Overview

Three critical issues were blocking the system from functioning end-to-end. This document details every file that was changed or created, what was wrong, and what was done to fix it.

---

## Fix 1 — CORS Middleware (Frontend ↔ Backend Connection)

### Problem
The FastAPI backend had **no CORS (Cross-Origin Resource Sharing) headers** configured. Modern browsers enforce a same-origin policy — any HTTP request made from the React frontend (`http://localhost:5173`) to the FastAPI backend (`http://localhost:8000`) would be silently **blocked by the browser** before reaching the server. This meant the entire frontend was non-functional even if the backend was running correctly.

### File Changed
`backend/app/main.py`

### What Changed

**Before:**
```python
app = FastAPI()
```

**After:**
```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trend Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Why These Specific Origins
- `http://localhost:5173` — default Vite dev server address
- `http://127.0.0.1:5173` — same server, alternate loopback address (some browsers treat these differently)

> **Production note:** Before deploying, replace these with your actual production frontend domain.

---

## Fix 2 — `/trends` Endpoint Wired to ML Results

### Problem
`trend_service.py` was querying the **`searches`** table (user search history) to populate the `/trends` endpoint. This table only stores raw queries typed by users — it has no ML analysis, no sentiment, no velocity, no meaningful trend data. The `/trends` page was essentially showing a search history leaderboard rather than actual ML-computed trends.

### Files Changed / Created

#### New File: `backend/app/models/ml_trend_result.py`
A new SQLAlchemy ORM model was created to map to the **`ml_trend_results`** table — the table the ML engine writes its output to after every pipeline run.

```python
class MLTrendResult(Base):
    __tablename__ = "ml_trend_results"

    id               = Column(Integer, primary_key=True)
    topic_id         = Column(Integer)
    keywords         = Column(String)       # comma-separated top keywords
    volume           = Column(Integer)      # post count in this cluster
    velocity         = Column(Float)        # growth rate vs previous run
    acceleration     = Column(Float)        # change in growth rate
    sentiment        = Column(Float)        # avg sentiment score (-1 to 1)
    sentiment_label  = Column(String(20))   # "positive" / "negative" / "neutral"
    positive_pct     = Column(Float)
    negative_pct     = Column(Float)
    neutral_pct      = Column(Float)
    top_posts        = Column(String)       # top 3 post titles
    subreddits       = Column(String)       # contributing subreddits
    avg_ups          = Column(Float)
    avg_comments     = Column(Float)
    score            = Column(Float)        # composite trend score
    run_at           = Column(DateTime)     # timestamp of this ML run
```

#### Rewritten: `backend/app/services/trend_service.py`

**Before:**
```python
def get_trends():
    db = SessionLocal()
    # getting top 5 searches sorted by highest trend score
    data = db.query(Search).order_by(Search.trend_score.desc()).limit(5).all()
    db.close()
    result = []
    for item in data:
        result.append({"query": item.query, "trend_score": item.trend_score})
    return result
```

**After:**
```python
def get_trends(limit: int = 10):
    db = SessionLocal()
    try:
        # Find the most recent ML run timestamp
        latest_run = db.execute(text("SELECT MAX(run_at) FROM ml_trend_results")).scalar()

        if latest_run is None:
            return {"trends": [], "message": "No ML results yet. Run the data pipeline first."}

        # Fetch top clusters from that run, ordered by composite score DESC
        data = (
            db.query(MLTrendResult)
            .filter(MLTrendResult.run_at == latest_run)
            .order_by(MLTrendResult.score.desc())
            .limit(limit)
            .all()
        )
        # ... serialise and return full trend data
    finally:
        db.close()
```

**What the response now includes (per trend topic):**

| Field | Description |
|-------|-------------|
| `topic_id` | Cluster ID assigned by the ML engine |
| `keywords` | Top 5 keywords for this topic cluster |
| `score` | Composite trend score (higher = more trending) |
| `volume` | Number of posts in this cluster |
| `velocity` | Growth rate compared to previous run |
| `acceleration` | Change in growth rate |
| `sentiment` | Average sentiment score (−1 to +1) |
| `sentiment_label` | `"positive"` / `"negative"` / `"neutral"` |
| `positive_pct` | % of posts with positive sentiment |
| `negative_pct` | % of posts with negative sentiment |
| `neutral_pct` | % of posts with neutral sentiment |
| `top_posts` | Top 3 post titles by upvotes |
| `subreddits` | Contributing subreddit names |
| `avg_ups` | Average upvotes across cluster |
| `avg_comments` | Average comments across cluster |
| `run_at` | ISO timestamp of the ML run |

---

## Fix 3 — `/region` Endpoint Wired to ML Results

### Problem
`region_service.py` was querying the `searches` table filtered by `region == state`. However, the `searches` table stores the region as `"Earth"` (a hardcoded placeholder from the broken `search_logic`). No actual geographic filtering was happening — the endpoint returned empty results for every state.

### File Rewritten
`backend/app/services/region_service.py`

**Before:**
```python
def get_region_trends(state: str):
    db = SessionLocal()
    data = db.query(Search)\
        .filter(Search.region == state)\
        .order_by(Search.trend_score.desc())\
        .limit(5).all()
    db.close()
    return [{"query": item.query, "trend_score": item.trend_score, "region": item.region} for item in data]
```

**After:**
The new implementation queries `ml_trend_results` and uses a **state-keyword mapping** to fuzzy-match subreddit names stored in the `subreddits` column:

```python
STATE_KEYWORDS = {
    "maharashtra": ["mumbai", "pune", "maharashtra", "marathi"],
    "delhi":       ["delhi", "newdelhi", "delhincr"],
    "karnataka":   ["bengaluru", "bangalore", "karnataka", "kannada"],
    "tamil nadu":  ["chennai", "tamilnadu", "tamil"],
    "west bengal": ["kolkata", "bengal", "bengali"],
    "telangana":   ["hyderabad", "telangana"],
    "gujarat":     ["ahmedabad", "gujarat", "gujarati"],
    "rajasthan":   ["jaipur", "rajasthan"],
    "kerala":      ["kerala", "kochi", "malayalam"],
    "uttar pradesh": ["lucknow", "noida", "up", "uttarpradesh"],
}
```

**Filtering logic:**
1. Map the requested state name to a list of regional keywords
2. For each keyword, run a case-insensitive `LIKE` query against the `subreddits` column
3. Deduplicate results (same topic may match multiple keywords)
4. **Fallback:** If no state-specific posts found, return global top trends for that run (ensures the frontend always gets data, never an empty page)

---

## Fix 4 — Search Score Placeholder Replaced

### Problem
`search_service.py` computed the trend score as:
```python
trend_score = len(query)   # e.g. "AI" → score of 2, "cricket" → score of 7
```
This was a string-length placeholder — a random number completely unrelated to actual trend popularity.

### File Changed
`backend/app/services/search_service.py`

**What was added:**
A private helper function `_lookup_ml_score(db, query)` that:
1. Finds the most recent ML run timestamp
2. Splits the user's query into individual words (ignoring words ≤ 2 characters)
3. For each word, runs a case-insensitive `LIKE` search against the `keywords` column of `ml_trend_results`
4. Returns the **highest matching cluster score** found
5. Falls back to `0.0` gracefully if no ML data exists yet

```python
def _lookup_ml_score(db, query: str) -> float:
    latest_run = db.execute(text("SELECT MAX(run_at) FROM ml_trend_results")).scalar()
    if latest_run is None:
        return 0.0

    words = [w.strip().lower() for w in query.split() if len(w.strip()) > 2]
    best_score = 0.0

    for word in words:
        match = (
            db.query(MLTrendResult)
            .filter(
                MLTrendResult.run_at == latest_run,
                MLTrendResult.keywords.ilike(f"%{word}%")
            )
            .order_by(MLTrendResult.score.desc())
            .first()
        )
        if match and match.score and match.score > best_score:
            best_score = match.score

    return round(best_score, 2)
```

Also fixed: the hardcoded `region="Earth"` was corrected to `region="Global"`.

---

## Fix 5 — Pydantic Schema Type Correction

### File Changed
`backend/app/schemas/search_schema.py`

**Before:**
```python
trend_score: int
```

**After:**
```python
trend_score: float
```

ML scores are decimal values (e.g. `42.75`). Using `int` would silently truncate the decimal portion during serialisation.

---

## Summary of All Changes

| File | Action | Reason |
|------|--------|--------|
| `backend/app/main.py` | Modified | Added CORS middleware |
| `backend/app/models/ml_trend_result.py` | **Created** | ORM model for `ml_trend_results` table |
| `backend/app/services/trend_service.py` | Rewritten | Query `ml_trend_results` instead of `searches` |
| `backend/app/services/region_service.py` | Rewritten | State-keyword filtering against `ml_trend_results` |
| `backend/app/services/search_service.py` | Modified | Replace `len(query)` with ML keyword score lookup |
| `backend/app/schemas/search_schema.py` | Modified | Change `trend_score` type from `int` to `float` |

---

## Dependency Note

All three API endpoints (`/search`, `/trends`, `/region`) now depend on the **`ml_trend_results`** table having data. The system will return empty results or `score: 0.0` gracefully until the ML pipeline runs at least once:

```bash
# Run the full pipeline (ETL + ML)
.\venv\Scripts\python.exe data_pipeline\schedulers\cron_jobs.py

# Or run just the ML engine
.\venv\Scripts\python.exe ml_engine\pipelines\ml_runner.py
```

See `RUN_GUIDE.md` for full setup instructions.
