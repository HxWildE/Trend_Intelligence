# ML Engine Data Flow & Architecture

This document outlines the entire life cycle of the `ml_engine` pipeline: how it ingests data, the algorithms applied, the technologies used, and what it ultimately outputs to the backend.

---

## 1. Technologies & Libraries Used

The ML Engine is built independently of the API but uses a shared data layer. It relies heavily on modern NLP and Data Science libraries:
* **Transformers:** `sentence-transformers` for generating dense semantic vector embeddings.
* **Scikit-Learn (`sklearn`):** Used for KMeans clustering and TF-IDF feature extraction.
* **NLTK (Natural Language Toolkit):** Used for rule-based sentiment analysis (VADER).
* **SQLAlchemy:** Used for high-performance chunked reads/writes to the PostgreSQL database.

---

## 2. Input: From Where and In What Format?

**Source Location:**
The `ml_engine` acts as an automated bridge (`ml_runner.py`). It does **not** rely on live API requests. Instead, it pulls raw data asynchronously from the `reddit_trends` PostgreSQL table, which is periodically filled by the Data Pipeline.

**Data Ingestion (`ml_runner.py`):**
1. Fetches the latest batch of posts (title, content, subreddits, upvotes, comments) from Postgres.
2. Fetches the *previous run's* cluster volumes to calculate rate of change (velocity/acceleration).
3. Constructs a combined array of texts (`"title. content"`) alongside rich metadata.

---

## 3. Processing Flow: Algorithms in Action

Once the text arrays are built, they pass through the **`TrendPipeline`**, which executes the following mathematical models in sequence:

### Step 1: Preprocessing + Sentiment Analysis (`SentimentInference`)
* **Algorithm:** NLTK VADER (Valence Aware Dictionary and sEntiment Reasoner).
* **Action:** Each post is cleaned (URLs, special characters, and numbers removed, then converted to lowercase). VADER then scores it between `-1.0` (negative) and `+1.0` (positive).
* **Reasoning:** VADER is specifically tuned for social media text and handles emojis, slang, and capitalization well without requiring GPU acceleration.

### Step 2: Sentence Embeddings (`EmbeddingModel`)
* **Algorithm:** dense vector embeddings via `sentence-transformers/all-MiniLM-L6-v2`.
* **Action:** Converts the cleaned English text into floating-point vectors (384 dimensions).
* **Reasoning:** `all-MiniLM-L6-v2` is a lightweight, highly optimized transformer model that maps semantically similar sentences close to each other in vector space, allowing the engine to recognize that a post about "Apple iPhone" and "iOS update" belong together.

### Step 3: Topic Clustering (`ClusterModel`)
* **Algorithm:** KMeans Clustering (`sklearn.cluster.KMeans`).
* **Action:** Groups the 384-dimensional vectors into distinct "topic clusters". The system dynamically scales from `n=1` up to a maximum of `K=8` clusters based on data volume.
* **Reasoning:** KMeans effectively partitions the space so that posts talking about the same broader topic are bundled under a single `topic_id`.

### Step 4: Topic Labeling (`TopicLabeler`)
* **Algorithm:** TF-IDF (Term Frequency-Inverse Document Frequency) (`sklearn.feature_extraction.text.TfidfVectorizer`).
* **Action:** Scans all posts within a specific cluster and extracts the **Top 5 most defining keywords**, automatically ignoring standard English stop-words ("the", "and", etc.).
* **Reasoning:** Allows the frontend to display human-readable labels (e.g., `["budget", "finance", "tax"]`) instead of internal cluster IDs.

### Step 5: Master Trend Scoring (`TrendScorer`)
* **Algorithm:** Custom Weighted Formula.
* **Action:** Aggregates the volume, historical velocity, historical acceleration, and average sentiment of the cluster into a single score:
  `Score = (0.35 * volume) + (0.30 * velocity) + (0.20 * acceleration) + (0.15 * sentiment * 10)`
* **Reasoning:** Ensures that a topic that is suddenly spiking (high acceleration) outranks a topic that is consistently popular but stagnant (high volume, zero velocity).

---

## 4. Output: To Where and In What Format?

**Destination:**
Once the `TrendPipeline` finishes structuring the clusters, `ml_runner.py` writes the enriched payload directly into the **`ml_trend_results`** table in PostgreSQL.

**Output Data Format (Database Schema):**
The API backend subsequently reads this table. Each row represents a single **Topic Cluster**, not an individual post.

```json
{
    "topic_id": 0,
    "keywords": "chennai, heavy, floods, rain",
    "volume": 120,
    "velocity": 5.4,
    "acceleration": 1.2,
    "sentiment": -0.85,
    "sentiment_label": "negative",
    "positive_pct": 10.0,
    "negative_pct": 80.0,
    "neutral_pct": 10.0,
    "subreddits": "india, chennai",
    "top_posts": "Heavy rain in Chennai causing floods || Cars submerged in T-Nagar",
    "avg_ups": 450.5,
    "avg_comments": 120.2,
    "score": 85.4,
    "run_at": "2025-05-18T10:00:00Z"
}
```

This single unified table serves as the "Source of Truth" for the FastAPI backend. Whenever the React Frontend hits `/trends` or `/region`, the backend simply queries `ml_trend_results`, ensuring the frontend remains lighting fast and completely unblocked by ML processing times.
