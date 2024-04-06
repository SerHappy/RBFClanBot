from .base import Base
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TEXT
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


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

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    status_id = Column(Integer, ForeignKey("application_statuses.id", ondelete="CASCADE"), default=1)
    decision_date = Column(TIMESTAMP)
    rejection_reason = Column(TEXT)
    invite_link = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="applications")
    status = relationship("ApplicationStatus", back_populates="applications")
    answers = relationship("ApplicationAnswer", back_populates="application")
    admin_applications = relationship("AdminProcessingApplication", back_populates="application")
