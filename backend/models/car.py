from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

class SearchCar(Base):
    __tablename__ = "search_cars"
    # Не допускаем повторного добавления одного объявления
    # в рамках одного и того же поиска.
    __table_args__ = (
        UniqueConstraint(
            "search_id",
            "car_id",
            name="uq_search_car"),
    )

    # Внутренний идентификатор записи
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True)

    # ID поиска, к которому относится автомобиль
    search_id: Mapped[int] = mapped_column(
        ForeignKey("searches.id", ondelete="CASCADE"),
        nullable=False)

    # ID объявления AUTO.RIA
    car_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False)

    # Тип автомобиля: electric или combustion
    car_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False)

    # Основные характеристики
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    year: Mapped[int | None] = mapped_column(Integer)
    mileage_km: Mapped[int | None] = mapped_column(Integer)

    gearbox: Mapped[str | None] = mapped_column(String(100))
    drive_type: Mapped[str | None] = mapped_column(String(100))

    # Цены
    price_usd: Mapped[float | None] = mapped_column(Float)
    price_uah: Mapped[float | None] = mapped_column(Float)

    # Дополнительные данные
    modification_name: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(Text)

    fuel_name: Mapped[str | None] = mapped_column(String(100))
    engine_volume_l: Mapped[float | None] = mapped_column(Float)

    # Полный исходный ответ AUTO.RIA по автомобилю
    raw_data: Mapped[dict | None] = mapped_column(JSON)

    # Связь с поиском
    search = relationship("Search", back_populates="cars")
