from app.db.connection import SessionLocal
from app.models.search import Search
from app.utils.logger import log


def search_logic(query: str):
    """
    Processes the search query, calculates a basic trend score based on its length,
    saves the search record to the database, and returns the result.

    Args:
        query (str): The search query phrase entered by the user.

    Returns:
        dict: A dictionary containing the query, the computed trend score, and a success message.
    """
    log(f"Search query: {query}")

    db = SessionLocal()

    trend_score = len(query)

    new_search = Search(
        query=query,
        trend_score=trend_score
    )

    db.add(new_search)
    db.commit()
    db.close()

    return {
        "query": query,
        "trend_score": trend_score,
        "message": "saved to DB"
    }


def call_ml(query: str):
    """
    Simulates a call to a machine learning engine to process the search query
    and return a trend prediction along with a confidence score.

    Args:
        query (str): The search query to be analyzed.

    Returns:
        dict: A simulated response containing a dummy trend and a mock confidence score.
    """
    # Simulated machine learning engine response (placeholder for real ML model)
    return {
        "trend": "dummy trend",
        "score": 0.95  # Mock confidence score
    }

# reads all data from database and returns it as JSON
def get_all_searches():
    """
    Retrieves all past search queries and their associated trend scores from the database.

    Returns:
        list: A list of dictionaries representing all saved search records in JSON-like format.
    """
    db = SessionLocal()

    data = db.query(Search).all()

    result = []
    for item in data:
        result.append({
            "id": item.id,
            "query": item.query,
            "trend_score": item.trend_score
        })

    db.close()
    return result


