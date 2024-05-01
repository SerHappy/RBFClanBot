from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    """User model for database table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        type_=BigInteger,
    )
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
    )

    applications = relationship(
        "Application",
        back_populates="user",
        order_by="Application.decision_date",
        cascade="all, delete",
    )
    admin_applications = relationship(
        "AdminProcessingApplication",
        back_populates="admin",
        cascade="all, delete",
    )
