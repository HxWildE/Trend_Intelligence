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

-- Stores pre-computed trend analysis results from the ML engine
CREATE TABLE IF NOT EXISTS ml_trend_results (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL,
    keywords TEXT,
    volume INTEGER,
    velocity FLOAT,
    acceleration FLOAT,
    sentiment FLOAT,
    sentiment_label VARCHAR(20),
    positive_pct FLOAT DEFAULT 0,
    negative_pct FLOAT DEFAULT 0,
    neutral_pct FLOAT DEFAULT 0,
    top_posts TEXT,
    subreddits TEXT,
    avg_ups FLOAT DEFAULT 0,
    avg_comments FLOAT DEFAULT 0,
    score FLOAT,
    run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);