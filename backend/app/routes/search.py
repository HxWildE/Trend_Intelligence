# Define API endpoints related to searching
from fastapi import APIRouter
from app.services.search_service import search_logic
from app.schemas.search_schema import SearchResponse
from app.services.search_service import get_all_searches
from app.services.search_service import get_search_by_id as service_get_search_by_id
from app.services.search_service import delete_search as service_delete_search

# Initialize the router for search endpoints
router = APIRouter()

# Define a GET route for /search that expects a query parameter 'q'
# The response will be validated against the SearchResponse schema
@router.get("/search", response_model=SearchResponse)
async def search(q: str):
    # Processes the search query via business logic and returns the response
    # Pass the query 'q' to the business logic layer and return the calculated result
    result = await search_logic(q)
    return result

@router.get("/all-searches")
def all_searches():
    # Retrieves the history of all searched queries from the DB
    return get_all_searches()

@router.get("/search/id/{search_id}")
def get_search_by_id(search_id: int):
    return service_get_search_by_id(search_id)


@router.delete("/search/id/{search_id}")
def delete_search(search_id: int):
    return service_delete_search(search_id)