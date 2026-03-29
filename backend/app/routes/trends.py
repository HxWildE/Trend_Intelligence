# Define API endpoints related to global trends
from fastapi import APIRouter

# Initialize the router for trend-related endpoints
router = APIRouter()

# Define a GET route for /trends to fetch current trending topics
@router.get("/trends")
def get_trends():
    """
    Fetches the current global trending topics.
    
    Returns:
        dict: A dictionary containing a list of top trending topics.
    """
    # Return a hardcoded list of global trends (to be replaced with dynamic data later)
    return {"trends": ["AI", "IPL", "Elections"]}