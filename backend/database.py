import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from backend.config import get_postgres_password

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("POSTGRES_USER", "postgres"),
    password=get_postgres_password(),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("POSTGRES_DB", "pet_parsing_ai"),)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()