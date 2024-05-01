from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.application.value_objects import ApplicationStatusEnum
from app.models.base import Base


class Application(Base):
    """Application model for database table."""

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        type_=BigInteger,
    )
    status: Mapped[ApplicationStatusEnum] = mapped_column(
        default=ApplicationStatusEnum.IN_PROGRESS,
        server_default=ApplicationStatusEnum.IN_PROGRESS,
    )
    decision_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    rejection_reason: Mapped[str] = mapped_column(String, nullable=True)
    invite_link: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
    )

    user = relationship("User", back_populates="applications")
    answers = relationship("ApplicationAnswer", back_populates="application")
    admin_applications = relationship(
        "AdminProcessingApplication",
        back_populates="application",
    )
