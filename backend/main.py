from fastapi import FastAPI
from backend.routers import health, dictionaries , searches , history


app = FastAPI(
    title="Pet Parsing AI API",
    description="Backend API for Pet Parsing AI",
    version="1.0.0"
)
app.include_router(health.router)
app.include_router(dictionaries.router)
app.include_router(searches.router)
app.include_router(history.router)