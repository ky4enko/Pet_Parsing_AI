from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database import get_db

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}