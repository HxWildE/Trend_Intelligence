# News API, NLP Summarization, and Dashboard Refactoring Tasks

- `[x]` **1. Configuration & Dependencies**
  - `[x]` Add `NEWS_API_KEY` to `.env` and `config.py`
  - `[x]` Install necessary NLP libraries (e.g., `transformers` or `nltk` for summarizer) in the backend.

- `[x]` **2. Data Pipeline Collectors**
  - `[x]` Create `data_pipeline/collectors/hacker_news_collector.py` (fetching top stories)
  - `[x]` Update `data_pipeline/collectors/news_collector.py` (fetching top NewsAPI headlines)
  - `[x]` Ensure both collectors can persist data to the Postgres database for the ML engine.

- `[x]` **3. Backend Real-Time News & NLP Service**
  - `[x]` Create `backend/app/services/nlp_summarizer.py`
  - `[x]` Create `backend/app/routes/news.py` to fetch, summarize, and serve live news
  - `[x]` Register the `news` router in `backend/app/main.py`

- `[x]` **4. ML Engine Update**
  - `[x]` Modify `ml_engine/pipelines/ml_runner.py` to also read from the news database table for long-term trend processing.

- `[x]` **5. Frontend Refactoring & Dashboard**
  - `[x]` Create shared UI Components (e.g., `NewsCard`, `Badge`)
  - `[x]` Create `NewsFeed.jsx` component that calls `/api/news/realtime`
  - `[x]` Refactor `GlobalTrends.jsx` to prominently feature the `NewsFeed` and clean up its layout.
