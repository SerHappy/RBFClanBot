from sqlalchemy import TEXT, TIMESTAMP, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"))
    question_number = Column(Integer)
    answer_text = Column(TEXT)
    created_at = Column(TIMESTAMP, server_default=func.now())

    application = relationship("Application", back_populates="answers", cascade="all, delete")
