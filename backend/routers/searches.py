from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.search import SearchRequest, SearchResult
from backend.services.search_service import SearchService



router = APIRouter(
    prefix="/searches",
    tags=["Searches"]
)
@router.post("/", response_model=SearchResult)
def create_search(
    payload: SearchRequest,
    db: Session = Depends(get_db)
):
    search_data = payload.model_dump(exclude={"language"})
    service = SearchService(db)
    result = service.search(
        search_data,
        language=payload.language)
    return result