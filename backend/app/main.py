# Main entry point for the FastAPI application
from fastapi import FastAPI
from app.routes import search

# Initialize the FastAPI app instance
app = FastAPI()

# Register the search router to include its endpoints in the main app
app.include_router(search.router)

# Define a simple health-check route at the root URL ("/")
@app.get("/")
def root():
    """
    Health-check endpoint for the API.

    Returns:
        dict: A status message indicating that the API is running correctly.
    """
    # Return a basic status message confirming the API is alive
    return {"status": "API running"}