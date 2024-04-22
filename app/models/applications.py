from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Application(Base):
    """
    Модель заявок от пользователей.

    Название таблицы: applications

    Поля:
    - id (Integer): идентификатор. Автоинкремент, первичный ключ
    - user_id (BigInteger): идентификатор пользователя. Внешний ключ на users.id
    - status_id (Integer): идентификатор статуса заявки. Внешний ключ на application_statuses.id
    - decision_date (TIMESTAMP): дата решения заявки
    - rejection_reason (TEXT): причина отклонения заявки
    - invite_link (String(255)): ссылка на приглашение
    - created_at (TIMESTAMP): дата создания записи
    """

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        type_=BigInteger,
    )
    status_id: Mapped[int] = mapped_column(
        ForeignKey("application_statuses.id", ondelete="CASCADE"),
        default=1,
    )
    decision_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    rejection_reason: Mapped[str]
    invite_link: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
    )

    user = relationship("User", back_populates="applications")
    status = relationship("ApplicationStatus", back_populates="applications")
    answers = relationship("ApplicationAnswer", back_populates="application")
    admin_applications = relationship(
        "AdminProcessingApplication", back_populates="application"
    )
