# Integrating Live News, NLP Summarization, and Frontend Refactoring

This implementation plan outlines how we will add global real-time news to the Trend Intelligence System dashboard, use NLP to generate bite-sized summaries of those news articles, and refactor the frontend codebase for a cleaner architecture.

## User Review Required

> [!IMPORTANT]
> **API Key Required:** To use NewsAPI, you will need to register for a free API key at [NewsAPI.org](https://newsapi.org). I will add a placeholder in your `.env` file, but you will need to fill it in for the News collector to work. 
> HackerNews does *not* require an API key.

> [!WARNING]
> **NLP Summarization Computation:** Running an NLP summarization model (like HuggingFace generic Transformers) on live news adds a slight delay to the API response. We will use a lightweight, fast model (e.g., `t5-small` or `distilbart-cnn`) to ensure the dashboard loads quickly.

## Proposed Changes

### Data Pipeline & Backend (Real-Time Live Feed & NLP)

#### [NEW] `data_pipeline/collectors/hacker_news_collector.py`
Creates a fast script that hits the `firebaseio` HackerNews API to retrieve the current top stories.

#### [MODIFY] `data_pipeline/collectors/news_collector.py`
Updates the placeholder file to use `requests` to fetch top headlines from NewsAPI, mapped to your configured keywords.

#### [NEW] `backend/app/services/nlp_summarizer.py`
A new lightweight service using the `transformers` library (or `nltk`/`sumy` if you prefer purely CPU-bound traditional NLP) that takes a news article's content and compresses it into a concise 1-2 sentence summary.

#### [NEW] `backend/app/routes/news.py`
A FastApi router that exposes `GET /api/news/realtime`. This endpoint fetches the top latest news from HackerNews/NewsAPI, passes the articles through the NLP summarizer, and returns the unified, summarized feed to the frontend.

#### [MODIFY] `backend/app/main.py`
Register the new `news` router.

---

### Machine Learning Engine

#### [MODIFY] `ml_engine/pipelines/ml_runner.py`
Updates the ML runner to pull data from not just the Reddit table, but also append fetched News/HackerNews data into the text clustering algorithm, allowing it to identify cross-platform trends.

---

### Frontend Refactoring & Dashboard Updates
We will clean up the React codebase and build a stunning new presentation for the news.

#### [MODIFY] `frontend/src/pages/GlobalTrends.jsx` & `IndiaTrends.jsx`
Refactor these large pages by stripping out duplicated code and moving logic into dedicated components. We will redesign the dashboard layout to prominently feature the Global Latest News at the top or center, rather than just burying it in a sidebar.

#### [NEW] `frontend/src/components/NewsFeed.jsx`
A sleek, modern component (e.g., masonry grid or carousel) for the live news. Each news card will display the headline, source, timestamp, and the **NLP-generated summary**.

#### [NEW] `frontend/src/components/shared/`
As part of the refactoring, build out shared UI components (like `Card.jsx`, `Badge.jsx`, `Layout.jsx`) to make the frontend modular and maintainable.

## Open Questions

1. **NewsAPI Tier:** Are you okay starting with the free tier constraints of NewsAPI (slightly delayed articles), or do you have a paid NewsAPI key? 
2. **NLP Summarization Approach:** Do you want me to use a deep-learning model (HuggingFace `transformers` - higher accuracy but requires heavier processing/RAM) or a traditional statistical NLP parser (like `nltk` TextRank - lightning fast but sometimes less grammatically perfect)?
3. **Data Storage:** Should we store these news articles in your Postgres database so the Machine Learning system can find long-term patterns, or would you prefer *only* a live, real-time feed?

## Verification Plan

### Automated Tests
- Test endpoints `GET /api/news/realtime` to verify valid JSON response containing `nlp_summary`.
- Verify the NLP summarizer returns a string less than 3 sentences.

### Manual Verification
- Start the React server and verify the new Dashboard layout visually pops.
- Confirm the `NewsFeed` component loads instantly and summarizes correctly.
- Ensure the refactored React components compile without errors.
