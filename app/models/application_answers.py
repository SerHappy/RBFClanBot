from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ApplicationAnswer(Base):
    """
    Модель ответов на вопросы.

    Название таблицы: application_answers

    Поля:
    - id (Integer): идентификатор. Автоинкремент, первичный ключ
    - application_id (Integer): идентификатор заявки. Внешний ключ на applications.id
    - question_number (Integer): порядковый номер вопроса
    - answer_text (TEXT): текст ответа
    - created_at (TIMESTAMP): дата создания записи

    """

    __tablename__ = "application_answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE")
    )
    question_number: Mapped[int]
    answer_text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
    )

    application = relationship(
        "Application", back_populates="answers", cascade="all, delete"
    )
