# Main entry point for the FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import search
from app.routes import health
from app.routes import trends
from app.routes import region
from app.routes import news
from app.models.search import Base
from app.db.connection import engine

# Initialize the FastAPI app instance
app = FastAPI(title="Trend Intelligence API", version="1.0.0")

# Allow the React dev server (and any other origin) to call the API.
# In production, replace "*" with your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


# Register the search router to include its endpoints in the main app
app.include_router(search.router)
app.include_router(health.router)
app.include_router(trends.router)
app.include_router(region.router)
app.include_router(news.router, tags=["News"])

# Define a simple health-check route at the root URL ("/")
@app.get("/")
def root():
    # Health-check endpoint to affirm the API is running
    # Return a basic status message confirming the API is alive
    return {"status": "API running"}