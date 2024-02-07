from .base import Base
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Users(Base):
    """Users model."""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    username = Column(String(32))
    first_name = Column(String(64))
    last_name = Column(String(64))
    is_admin = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    applications = relationship("Applications", back_populates="user")
