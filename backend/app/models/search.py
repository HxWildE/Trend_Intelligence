from sqlalchemy import Column, Integer, String
from app.db.connection import engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Search(Base):
    """
    SQLAlchemy model representing a search record in the database.
    Stores the search query and its corresponding trend score.
    """
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String)
    trend_score = Column(Integer)

Base.metadata.create_all(bind=engine)