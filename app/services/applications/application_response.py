from loguru import logger

from app.db.engine import UnitOfWork
from app.domain.application.exceptions import (
    ApplicationAnswerAlreadyExistError,
    ApplicationDoesNotExistError,
)
from app.domain.application_answers.dto import AnswerDTO
from app.domain.application_answers.entities import ApplicationAnswer
from app.services.applications.dto import (
    ApplicationResponseInputDTO,
    ApplicationResponseOutputStatusDTO,
)
from app.services.applications.value_objects import ApplicationResponseStatusEnum


class ApplicationResponseService:
    """Responsible for application response."""

    def __init__(self, uow: UnitOfWork) -> None:
        """
        Initialize the service instance.

        Args:
            uow (UnitOfWork): The unit of work instance.

        Returns:
            None
        """
        self._uow = uow

    async def execute(
        self,
        data: ApplicationResponseInputDTO,
    ) -> ApplicationResponseOutputStatusDTO:
        """
        Execute the application response service.

        Args:
            data (ApplicationResponseInputDTO): The data of the application response.

        Returns:
            ApplicationResponseOutputStatusDTO: The status of the application response.
        """
        async with self._uow():
            try:
                user_application = await self._uow.application.retrieve_last(
                    data.user_id,
                )
            except ApplicationDoesNotExistError as e:
                logger.critical(f"Got answer for non-existent application: {e}")
                raise
            answer_dto = AnswerDTO(
                application_id=user_application.id,
                question_number=data.question_number,
                answer_text=data.answer_text,
            )
            answer = ApplicationAnswer(answer_dto)
            try:
                user_application.add_new_answer(answer)
                await self._uow.application_answer.add_answer(answer)
                await self._uow.commit()
                return ApplicationResponseOutputStatusDTO(
                    status=ApplicationResponseStatusEnum.NEW,
                )
            except ApplicationAnswerAlreadyExistError:
                user_application.update_answer(answer)
                await self._uow.application_answer.update_answer(answer)
                await self._uow.commit()
                return ApplicationResponseOutputStatusDTO(
                    status=ApplicationResponseStatusEnum.UPDATE,
                )
