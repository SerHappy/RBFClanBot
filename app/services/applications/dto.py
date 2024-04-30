from pydantic import BaseModel

from app.services.applications.value_objects import ApplicationResponseStatusEnum


class ApplicationResponseInputDTO(BaseModel):
    """DTO for application response."""

    user_id: int
    answer_text: str
    question_number: int


class ApplicationResponseOutputStatusDTO(BaseModel):
    """DTO for application response output status."""

    status: ApplicationResponseStatusEnum
