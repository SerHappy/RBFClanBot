from domain.application_answers.entities import (
    ApplicationAnswer as ApplicationAnswerEntity,
)
from models import ApplicationAnswer
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from .abstract import Repository


class ApplicationAnswerRepository(Repository[ApplicationAnswer]):
    """Репозиторий для работы с ответами на заявки."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=ApplicationAnswer, session=session)

    async def add_answer(
        self,
        answer: ApplicationAnswerEntity,
    ) -> ApplicationAnswerEntity:
        """Создание ответа на заявку."""
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
        """Обновление ответа на вопрос."""
        statement = (
            update(ApplicationAnswer)
            .where(ApplicationAnswer.application_id == answer.application_id)
            .where(ApplicationAnswer.question_number == answer.question_number)
            .values(answer_text=answer.answer_text)
        )
        await self.session.execute(statement)

        return answer
