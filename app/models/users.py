from datetime import datetime

from sqlalchemy import TIMESTAMP, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))
    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
    )

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
