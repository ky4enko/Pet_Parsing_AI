from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base
from sqlalchemy.orm import relationship

class Search(Base):
    __tablename__ = "searches"

    # Уникальный идентификатор поиска
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True)

    # Дата и время создания поиска
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False)

    # Текущий статус поиска
    status: Mapped[str] = mapped_column(
        String(20),
        default="processing",
        nullable=False)

    # Все параметры и фильтры поиска
    search_params: Mapped[dict] = mapped_column(
        JSON,
        nullable=False)

    # Полный ответ GPT
    gpt_analysis: Mapped[str | None] = mapped_column(
        Text,
        nullable=True)

    # Название использованной GPT-модели
    gpt_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True)

    cars = relationship(
        "SearchCar",
        back_populates="search",
        cascade="all, delete-orphan"
    )

