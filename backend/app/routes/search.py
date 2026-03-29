# Define API endpoints related to searching
from fastapi import APIRouter
from app.services.search_service import search_logic
from app.schemas.search_schema import SearchResponse
from app.services.search_service import get_all_searches

# Initialize the router for search endpoints
router = APIRouter()

# Define a GET route for /search that expects a query parameter 'q'
# The response will be validated against the SearchResponse schema
@router.get("/search", response_model=SearchResponse)
def search(q: str):
    """
    Handles search requests by taking a query string, processing it via the business logic layer,
    and returning the generated search response.

    Args:
        q (str): The search query parameter.

    Returns:
        SearchResponse: The validated search response containing query, trend score, and message.
    """
    # Pass the query 'q' to the business logic layer and return the calculated result
    result = search_logic(q)
    return result

@router.get("/all-searches")
def all_searches():
    """
    Retrieves the history of all searched queries stored in the database.

    Returns:
        list: A JSON-serializable list of all past searches and their associated scores.
    """
    return get_all_searches()