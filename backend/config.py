import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def get_auto_ria_api_key() -> str:
    api_key = os.getenv("AUTO_RIA_API")
    if not api_key:
        raise ValueError("AUTO_RIA_API is not configured in .env")
    return api_key

def get_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured in .env")
    return api_key

# Папка для сохранения результатов поиска
SEARCH_DIR = BASE_DIR / "search"

def get_postgres_password() -> str:
    password = os.getenv("POSTGRES_PASSWORD")

    if not password:
        raise ValueError("POSTGRES_PASSWORD is not configured in .env")

    return password