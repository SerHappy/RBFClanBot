from dataclasses import dataclass
from enum import StrEnum


@dataclass
class ApplicationResponseDTO:
    """DTO for application response."""

    user_id: int
    answer_text: str
    question_number: int


class ApplicationResponseStatusEnum(StrEnum):
    """Enum for application response status."""

    NEW = "NEW"
    UPDATE = "UPDATE"


@dataclass
class ApplicationResponseOutputStatusDTO:
    """DTO for application response output status."""

    status: ApplicationResponseStatusEnum


@dataclass
class ApplicationUserDecisionInputDTO:
    """DTO for application user decision input."""
