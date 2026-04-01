"""
SQLAlchemy ORM model for the ml_trend_results table.

This table is written by the ML engine (ml_runner.py) and read
by the API to serve /trends and /region endpoints.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MLTrendResult(Base):
    """Represents one topic cluster produced by the ML engine."""

    __tablename__ = "ml_trend_results"

    id               = Column(Integer, primary_key=True, index=True)
    topic_id         = Column(Integer, nullable=False)
    keywords         = Column(String)          # comma-separated top keywords
    volume           = Column(Integer)         # number of posts in cluster
    velocity         = Column(Float)           # growth rate vs prev run
    acceleration     = Column(Float)           # change in growth rate
    sentiment        = Column(Float)           # avg sentiment score (-1 to 1)
    sentiment_label  = Column(String(20))      # "positive" / "negative" / "neutral"
    positive_pct     = Column(Float, default=0)
    negative_pct     = Column(Float, default=0)
    neutral_pct      = Column(Float, default=0)
    top_posts        = Column(String)          # top 3 post titles (serialised)
    subreddits       = Column(String)          # contributing subreddits
    avg_ups          = Column(Float, default=0)
    avg_comments     = Column(Float, default=0)
    score            = Column(Float)           # composite trend score
    run_at           = Column(DateTime)        # timestamp of this ML run
