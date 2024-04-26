from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AdminProcessingApplication(Base):
    """Модель связи админа и обрабатываемой им заявки."""

    __tablename__ = "admin_processing_applications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        type_=BigInteger,
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
    )

    admin = relationship("User", back_populates="admin_applications")
    application = relationship("Application", back_populates="admin_applications")
