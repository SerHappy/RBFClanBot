from .base import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


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

    id = Column(Integer, primary_key=True)
    status = Column(String(266))
    created_at = Column(TIMESTAMP, server_default=func.now())

    applications = relationship("Application", back_populates="status")
