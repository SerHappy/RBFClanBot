from dataclasses import dataclass


@dataclass
class AnswerDTO:
    """Data transfer object for application answers."""

    id: int
    application_id: int
    question_number: int
    answer_text: str
