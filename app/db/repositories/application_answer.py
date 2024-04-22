from collections.abc import Sequence

from loguru import logger
from models import ApplicationAnswer
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .abstract import Repository


class ApplicationAnswerRepository(Repository[ApplicationAnswer]):
    """Репозиторий для работы с ответами на заявки."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=ApplicationAnswer, session=session)

    async def create(
        self,
        application_id: int,
        question_number: int,
        answer_text: str | None = None,
    ) -> ApplicationAnswer:
        """Создание ответа на заявку.

        Args:
            application_id: ID заявки.
            question_number: Номер вопроса.
            answer_text: Текст ответа (Optional).

        Returns:
            Экземпляр ApplicationAnswer (созданный).
        """
        logger.debug(
            f"Создание ответа на заявку для application_id={application_id} и question_number={question_number} с текстом text={answer_text}"
        )
        answer = await self.session.merge(
            self.model(
                application_id=application_id,
                question_number=question_number,
                answer_text=answer_text,
            )
        )
        logger.debug(
            f"Создан ответ на заявку для application_id={application_id} и question_number={question_number}"
        )
        return answer

    async def get_application_answer_text_by_question_number(
        self,
        application_id: int,
        question_number: int,
    ) -> str | None:
        """
        Получение текста ответа по номеру вопроса у заданной заявки.

        Args:
            application_id: ID заявки.
            question_number: Номер вопроса.

        Returns:
            Текст ответа или None.
        """
        logger.debug(
            f"Получение текста ответа для application_id={application_id} и question_number={question_number}"
        )
        statement = (
            select(ApplicationAnswer)
            .where(ApplicationAnswer.application_id == application_id)
            .where(ApplicationAnswer.question_number == question_number)
        )

        answer = (await self.session.execute(statement)).scalar()
        if answer is None:
            logger.debug(
                f"Не найден ответ для application_id={application_id} и question_number={question_number}"
            )
            return None
        logger.debug(
            f"Найден ответ для application_id={application_id} и question_number={question_number}, возвращаем текст"
        )
        return answer.answer_text

    async def get_all_answers_by_application_id(
        self,
        application_id: int,
    ) -> Sequence[ApplicationAnswer]:
        """Получение всех ответов заявки.

        Args:
            application_id: ID заявки.

        Returns:
            Список экземпляров ApplicationAnswer.
        """
        logger.debug(f"Получение всех ответов для application_id={application_id}")
        statement = (
            select(ApplicationAnswer)
            .where(ApplicationAnswer.application_id == application_id)
            .order_by(ApplicationAnswer.question_number)
        )
        answers = (await self.session.execute(statement)).scalars().all()

        logger.debug(f"Получены все ответы для application_id={application_id}")
        return answers

    async def update_question_answer(
        self, application_id: int, question_number: int, answer_text: str
    ) -> None:
        """Обновление ответа на вопрос.

        Args:
            application_id: ID заявки.
            question_number: Номер вопроса.
            answer_text: Новый текст ответа.

        Returns:
            None
        """
        logger.debug(
            f"Обновление ответа на вопрос для application_id={application_id} и question_number={question_number}"
        )
        statement = (
            update(ApplicationAnswer)
            .where(ApplicationAnswer.application_id == application_id)
            .where(ApplicationAnswer.question_number == question_number)
            .values(answer_text=answer_text)
        )
        await self.session.execute(statement)
        logger.debug(
            f"Обновлен ответ на вопрос для application_id={application_id} и question_number={question_number}. Новый текст: {answer_text}"
        )
        return None

    async def delete_all_answers_by_application_id(self, application_id: int) -> None:
        """Удаление всех ответов для заявки.

        Args:
            application_id: ID заявки.

        Returns:
            None
        """
        logger.debug(f"Удаление всех ответов для application_id={application_id}")
        statement = delete(ApplicationAnswer).where(
            ApplicationAnswer.application_id == application_id
        )
        await self.session.execute(statement)
        logger.debug(f"Удалены все ответы для application_id={application_id}")
