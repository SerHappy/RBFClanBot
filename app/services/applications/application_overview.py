from app.db.engine import UnitOfWork


class ApplicationOverviewService:
    """Responsible for application overview."""

    def __init__(self, uow: UnitOfWork) -> None:
        """
        Initialize the service instance.

        Args:
            uow (UnitOfWork): The unit of work instance.

        Returns:
            None
        """
        self._uow = uow

    async def execute(self, user_id: int) -> str:
        """
        Execute the application overview service.

        Args:
            user_id (int): Telegram ID of the user.

        Raises:
            ApplicationDoesNotExistError: If the application does not exist.

        Returns:
            str: The application overview.
        """
        async with self._uow():
            user_application = await self._uow.application.retrieve_last(user_id)
        answers = user_application.answers
        overview_parts = []
        questions = {
            1: "PUBG ID",
            2: "Возраст",
            3: "Режимы игры",
            4: "Активность",
            5: "О себе",
        }

        for question_number in sorted(answers.keys()):
            answer = answers[question_number]
            question_text = questions.get(question_number)
            overview_parts.append(
                f"{question_number}) {question_text}: {answer.answer_text}",
            )
        overview_text = "\n".join(overview_parts)
        return f"Твоя заявка:\n\n{overview_text}\n\nВсе верно?"
