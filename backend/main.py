from fastapi import FastAPI, Depends

from backend.security import verify_api_token
from backend.routers import health, dictionaries, searches, history


app = FastAPI(
    title="Pet Parsing AI API",
    description="Backend API for Pet Parsing AI",
    version="1.0.0",
    dependencies=[Depends(verify_api_token)]
)

app.include_router(health.router)
app.include_router(dictionaries.router)
app.include_router(searches.router)
app.include_router(history.router)