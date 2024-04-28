from dataclasses import dataclass


@dataclass
class AnswerDTO:
    """Data transfer object for application answers."""

    application_id: int
    question_number: int
    answer_text: str
