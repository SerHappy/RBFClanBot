from .abstract import Repository
from collections.abc import Sequence
from loguru import logger
from models import ApplicationAnswer
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


class ApplicationAnswerRepository(Repository[ApplicationAnswer]):
    """ApplicationAnswer repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ApplicationAnswer repository."""
        super().__init__(type_model=ApplicationAnswer, session=session)

    async def create(
        self,
        application_id: int,
        question_number: int,
        answer_text: str | None = None,
    ) -> ApplicationAnswer:
        """Create new application answer.

        Args:
            application_id: Application id.
            question_number: Question number.
            answer_text: Answer text (Optional).

        Returns:
            ApplicationAnswer.
        """
        logger.debug(
            f"Creating application answer for application_id={application_id}, question_number={question_number} and answer_text={answer_text}"
        )
        new_answer = await self.session.merge(
            self.type_model(
                application_id=application_id,
                question_number=question_number,
                answer_text=answer_text,
            )
        )
        return new_answer

    async def get_answer_by_question_number(
        self,
        application_id: int,
        question_number: int,
    ) -> str | None:
        """Get answer by question number.

        Args:
            application_id: Application id.
            question_number: Question number.

        Returns:
            str or None.
        """
        logger.debug(f"Getting answer for application_id={application_id} and question_number={question_number}")
        statement = (
            select(ApplicationAnswer)
            .where(ApplicationAnswer.application_id == application_id)
            .where(ApplicationAnswer.question_number == question_number)
        )
        res = (await self.session.execute(statement)).scalar()
        if res is None:
            return None
        return res.answer_text

    async def get_all_answers_by_application_id(
        self,
        application_id: int,
    ) -> Sequence[ApplicationAnswer]:
        """Get all answers by application id.

        Args:
            application_id: Application id.

        Returns:
            Sequence of ApplicationAnswer.
        """
        logger.debug(f"Getting all answers for application_id={application_id}")
        statement = (
            select(ApplicationAnswer)
            .where(ApplicationAnswer.application_id == application_id)
            .order_by(ApplicationAnswer.question_number)
        )
        res = (await self.session.execute(statement)).scalars().all()
        return res

    async def update_question_answer(self, application_id: int, question_number: int, answer_text: str) -> None:
        """Update question answer.

        Args:
            application_id: Application id.
            question_number: Question number.
            answer_text: Answer text.
        """
        logger.debug(
            f"Updating question answer={answer_text} for application_id={application_id} and question_number={question_number}"
        )
        statement = (
            update(ApplicationAnswer)
            .where(ApplicationAnswer.application_id == application_id)
            .where(ApplicationAnswer.question_number == question_number)
            .values(answer_text=answer_text)
        )
        await self.session.execute(statement)
        return None

    async def delete_all_answers_by_application_id(self, application_id: int) -> None:
        """Delete all answers by application id.

        Args:
            application_id: Application id.
        """
        logger.debug(f"Deleting all answers for application_id={application_id}")
        statement = delete(ApplicationAnswer).where(ApplicationAnswer.application_id == application_id)
        await self.session.execute(statement)
