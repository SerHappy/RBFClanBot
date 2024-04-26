from dataclasses import dataclass
from datetime import datetime

from app.domain.application.value_objects import ApplicationStatusEnum


@dataclass(kw_only=True)
class ApplicationDTO:
    """Data transfer object for an application."""

    id: int
    user_id: int
    decision_date: datetime | None = None
    rejection_reason: str | None = None
    invite_link: str | None = None
    status: ApplicationStatusEnum
