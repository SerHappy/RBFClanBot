from .base import Base
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import TEXT
from sqlalchemy.orm import relationship


class ApplicationAnswer(Base):
    """ApplicationAnswers model."""

    __tablename__ = "application_answers"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    question_number = Column(Integer)
    answer_text = Column(TEXT)

    application = relationship("Application", back_populates="answers", cascade="all, delete")
