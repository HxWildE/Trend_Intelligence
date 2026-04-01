import json
import redis
from fastapi import APIRouter
from app.services.search_service import search_logic
from app.schemas.search_schema import SearchResponse
from app.services.search_service import get_all_searches
from app.services.search_service import get_search_by_id as service_get_search_by_id
from app.services.search_service import delete_search as service_delete_search

# Initialize the router for search endpoints
router = APIRouter()

# Setup Redis connection
try:
    redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
except Exception:
    redis_conn = None

# Define a GET route for /search that expects a query parameter 'q'
# The response will be validated against the SearchResponse schema
@router.get("/search", response_model=SearchResponse)
async def search(q: str):
    query = q.strip().lower()
    
    # 1. ⚡ Check Redis Cache (O(1) lookup)
    if redis_conn:
        cached_result = redis_conn.get(f"search:{query}")
        if cached_result:
            return json.loads(cached_result)

    # 2. ⚡ Process the fast live fallback (Cache Miss)
    result = await search_logic(query)

    # 3. ⚡ Enqueue Heavy ML Task to Background Worker via Redis
    if redis_conn:
        # Pushes Job to Redis List "search_queue" via rq
        try:
            from rq import Queue
            import redis as raw_redis
            
            # RQ strictly requires bytes, so we create a native non-decoded connection
            rq_redis = raw_redis.Redis(host='localhost', port=6379, db=0)
            q = Queue('search_queue', connection=rq_redis)
            q.enqueue("worker.run_search_ml_pipeline", query, job_timeout=300)
        except Exception as e:
            print(f"RQ Enqueue Error: {e}")

    # 4. ⚡ Update Redis Cache (TTL = 60 seconds)
    if redis_conn:
        redis_conn.setex(f"search:{query}", 60, json.dumps(result))

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