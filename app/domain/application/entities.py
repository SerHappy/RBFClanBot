from app.domain.application.dto import ApplicationDTO
from app.domain.application.exceptions import (
    ApplicationAlreadyCompleteError,
    ApplicationAnswerAlreadyExistError,
    ApplicationAnswerDoesNotExistError,
    ApplicationDoesNotCompeteError,
    ChangeApplicationStatusError,
)
from app.domain.application.value_objects import (
    ApplicationQuestionEnum,
    ApplicationStatusEnum,
)
from app.domain.application_answers.entities import ApplicationAnswer


class Application:
    """Represents an application domain object.

    Provides methods to change status, manage the answers.
    """

    def __init__(
        self,
        data: ApplicationDTO,
        answers: dict[int, ApplicationAnswer] | None = None,
    ) -> None:
        """Initialize the application instance."""
        self.id = data.id
        self.user_id = data.user_id
        self.status = data.status
        self.decision_date = data.decision_date
        self.invite_link = data.invite_link
        self.rejection_reason = data.rejection_reason
        self.answers = answers if answers else {}

    def add_new_answer(self, answer: ApplicationAnswer) -> None:
        """Add a new answer to the application."""
        if answer.question_number in self.answers:
            raise ApplicationAnswerAlreadyExistError

        self.answers[answer.question_number] = answer

    def update_answer(self, answer: ApplicationAnswer) -> None:
        """Update an existing answer in the application."""
        if answer.question_number not in self.answers:
            raise ApplicationAnswerDoesNotExistError

        self.answers[answer.question_number] = answer

    def clear(self) -> None:
        """Remove all answers from the application."""
        if self.status != ApplicationStatusEnum.IN_PROGRESS:
            raise ApplicationAlreadyCompleteError

        self.answers = {}

    def complete(self) -> None:
        """Change the application status to 'WAITING'."""
        if not self._check_is_all_answers_filled():
            raise ApplicationDoesNotCompeteError

        if self.status != ApplicationStatusEnum.IN_PROGRESS:
            raise ChangeApplicationStatusError

        self.status = ApplicationStatusEnum.WAITING

    def take(self) -> None:
        """Change the application status to 'PROCESSING'."""
        if self.status != ApplicationStatusEnum.WAITING:
            raise ChangeApplicationStatusError

        self.status = ApplicationStatusEnum.PROCESSING

    def accept(self) -> None:
        """Change the application status to 'ACCEPTED'."""
        if self.status != ApplicationStatusEnum.PROCESSING:
            raise ChangeApplicationStatusError

        self.status = ApplicationStatusEnum.ACCEPTED

    def reject(self) -> None:
        """Change the application status to 'REJECTED'."""
        if self.status != ApplicationStatusEnum.PROCESSING:
            raise ChangeApplicationStatusError

        self.status = ApplicationStatusEnum.REJECTED

    def _check_is_all_answers_filled(self) -> bool:
        """Check if all answers are filled."""
        return set(self.answers.keys()) == set(ApplicationQuestionEnum.all_ids())
