from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class User(Base):
    """
    Модель пользователей.

    Название таблицы: users

    Поля:
    - id (BigInteger): идентификатор. Равен telegram_id, Первичный ключ
    - username (String(255)): имя пользователя
    - first_name (String(64)): имя
    - last_name (String(64)): фамилия
    - created_at (TIMESTAMP): дата создания записи
    - is_banned (Boolean): забанен ли пользователь. По умолчанию False
    """

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    username = Column(String(255))
    first_name = Column(String(64))
    last_name = Column(String(64))
    is_banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    applications = relationship(
        "Application",
        back_populates="user",
        order_by="Application.decision_date",
        cascade="all, delete",
    )
    admin_applications = relationship(
        "AdminProcessingApplication",
        back_populates="admin",
        cascade="all, delete",
    )
