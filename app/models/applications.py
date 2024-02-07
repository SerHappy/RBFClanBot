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


class Applications(Base):
    """Applications model."""

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    status_id = Column(Integer, ForeignKey("application_statuses.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())
    submission_at = Column(TIMESTAMP)
    decision_date = Column(TIMESTAMP)
    rejection_reason = Column(TEXT)
    invite_link = Column(String(255))

    user = relationship("User", back_populates="applications")
    status = relationship("ApplicationStatus", back_populates="applications")
    answers = relationship("ApplicationAnswers", back_populates="application")
