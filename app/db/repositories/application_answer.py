from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.abstract import Repository
from app.domain.application_answers.entities import (
    ApplicationAnswer as ApplicationAnswerEntity,
)
from app.models import ApplicationAnswer


class ApplicationAnswerRepository(Repository[ApplicationAnswer]):
    """
    Responsible for working with the database.

    Manages operations on ApplicationAnswer objects.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            session (AsyncSession): The database session.

        Returns:
            None
        """
        super().__init__(type_model=ApplicationAnswer, session=session)

    async def add_answer(
        self,
        answer: ApplicationAnswerEntity,
    ) -> ApplicationAnswerEntity:
        """
        Insert new answer into database and return it.

        Args:
            answer (ApplicationAnswerEntity): The answer to insert.

        Returns:
            ApplicationAnswerEntity: The inserted answer.
        """
        query = insert(self.model).values(
            application_id=answer.application_id,
            question_number=answer.question_number,
            answer_text=answer.answer_text,
        )
        await self.session.execute(query)
        return answer

    async def update_answer(
        self,
        answer: ApplicationAnswerEntity,
    ) -> ApplicationAnswerEntity:
        """
        Update an existing answer in the database.

        Args:
            answer (ApplicationAnswerEntity): The answer to update.

        Returns:
            ApplicationAnswerEntity: The updated answer.
        """
        statement = (
            update(ApplicationAnswer)
            .where(ApplicationAnswer.application_id == answer.application_id)
            .where(ApplicationAnswer.question_number == answer.question_number)
            .values(answer_text=answer.answer_text)
        )
        await self.session.execute(statement)

        return answer
