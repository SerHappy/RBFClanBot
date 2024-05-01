from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ApplicationAnswer(Base):
    """ApplicationAnswer model for database table."""

    __tablename__ = "application_answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
    )
    question_number: Mapped[int]
    answer_text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', NOW())"),
    )

    application = relationship(
        "Application",
        back_populates="answers",
        cascade="all, delete",
    )
