from .base import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class ApplicationStatus(Base):
    """ApplicationStatus model."""

    __tablename__ = "application_statuses"

    id = Column(Integer, primary_key=True)
    status = Column(String(266))

    applications = relationship("Applications", back_populates="status")
