from app.domain.application_answers.dto import AnswerDTO


class ApplicationAnswer:
    """Represents an application answer domain object."""

    def __init__(self, data: AnswerDTO) -> None:
        """Initialize the application answer instance."""
        self.application_id = data.application_id
        self.answer_text = data.answer_text
        self.question_number = data.question_number
