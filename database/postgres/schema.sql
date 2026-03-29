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