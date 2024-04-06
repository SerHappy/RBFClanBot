from .base import Base
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship


class AdminProcessingApplication(Base):
    """Модель связи админа и обрабатываемой им заявки."""

    __tablename__ = "admin_processing_applications"

    id = Column(Integer, primary_key=True)
    admin_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"))

    admin = relationship("User", back_populates="admin_applications")
    application = relationship("Application", back_populates="admin_applications")
