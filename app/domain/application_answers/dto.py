from pydantic import BaseModel, ConfigDict


class AnswerDTO(BaseModel):
    """Data transfer object for application answers."""

    model_config = ConfigDict(from_attributes=True)

    application_id: int
    question_number: int
    answer_text: str
