from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.repositories.search_repository import SearchRepository
from backend.schemas.search import SearchHistoryItem, SearchRead


router = APIRouter(
    prefix="/history",
    tags=["History"])

@router.get("/", response_model=list[SearchHistoryItem])
def get_search_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    repository = SearchRepository(db)
    return repository.get_history(skip=skip, limit=limit)

@router.get("/{search_id}", response_model=SearchRead)
def get_search_details(
    search_id: int,
    db: Session = Depends(get_db)
):
    repository = SearchRepository(db)
    search = repository.get_by_id(search_id)
    if search is None:
        raise HTTPException(
            status_code=404,
            detail="Search not found")
    return search