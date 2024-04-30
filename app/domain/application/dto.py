from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.application.value_objects import ApplicationStatusEnum


class ApplicationDTO(BaseModel):
    """Data transfer object for an application."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    decision_date: datetime | None = None
    rejection_reason: str | None = None
    admin_id: int | None = None
    invite_link: str | None = None
    status: ApplicationStatusEnum
