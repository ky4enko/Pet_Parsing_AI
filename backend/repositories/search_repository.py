from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from backend.models import Search, SearchCar

class SearchRepository:

    def __init__(self, db: Session):
        self.db = db
    # Создание нового поиска
    def create_search(self, search_params: dict) -> Search:
        search = Search(
            search_params=search_params,
            status="processing")

        self.db.add(search)
        self.db.commit()
        self.db.refresh(search)
        return search

    # Сохранение найденных автомобилей
    def add_cars(self, search_id: int, cars: list[dict]) -> None:
        records = [
            SearchCar(search_id=search_id, **car_data)
            for car_data in cars
        ]

        self.db.add_all(records)
        self.db.commit()

    # Завершение поиска и сохранение анализа GPT
    def complete_search(
        self,
        search_id: int,
        gpt_analysis: str,
        gpt_model: str
    ) -> Search | None:

        search = self.db.get(Search, search_id)

        if search is None:
            return None

        search.gpt_analysis = gpt_analysis
        search.gpt_model = gpt_model
        search.status = "completed"

        self.db.commit()
        self.db.refresh(search)
        return search

    # Получение конкретного поиска вместе с автомобилями
    def get_by_id(self, search_id: int) -> Search | None:
        statement = (
            select(Search)
            .options(selectinload(Search.cars))
            .where(Search.id == search_id))
        return self.db.execute(statement).scalar_one_or_none()

    # Получение истории поисков
    def get_history(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> list[Search]:

        statement = (
            select(Search)
            .order_by(Search.created_at.desc())
            .offset(skip)
            .limit(limit))
        return list(self.db.scalars(statement).all())

    def fail_search(self, search_id: int):
        search = self.db.get(Search, search_id)
        if search is None:
            raise ValueError(
                f"Search with ID {search_id} not found"
            )
        search.status = "failed"
        self.db.commit()
        self.db.refresh(search)
        return search
