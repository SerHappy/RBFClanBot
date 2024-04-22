from datetime import datetime

from sqlalchemy import TIMESTAMP, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ApplicationStatus(Base):
    """
    Модель статусов заявок.

    Название таблицы: application_statuses

    Поля:
    - id (Integer): идентификатор. Автоинкремент, первичный ключ
    - status (String(266)): название статуса
    - created_at (TIMESTAMP): дата создания записи
    """

    __tablename__ = "application_statuses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
    )

    applications = relationship("Application", back_populates="status")
