# Define Pydantic request/response schemas for data validation
from pydantic import BaseModel

# Schema defining the structure and data types of a search response
class SearchResponse(BaseModel):
    query: str         # The original search term typed by the user
    trend_score: int   # The calculated popularity/trend score for the query
    message: str       # A status message indicating the processing result