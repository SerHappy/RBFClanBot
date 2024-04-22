from sqlalchemy import BigInteger, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class AdminProcessingApplication(Base):
    """Модель связи админа и обрабатываемой им заявки."""

    __tablename__ = "admin_processing_applications"

    id = Column(Integer, primary_key=True)
    admin_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"))

    admin = relationship("User", back_populates="admin_applications")
    application = relationship("Application", back_populates="admin_applications")
