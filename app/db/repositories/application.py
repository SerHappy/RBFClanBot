from models import Application
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.application.dto import ApplicationDTO
from app.domain.application.entities import Application as ApplicationEntity
from app.domain.application.exceptions import (
    ApplicationAlreadyExistsError,
    ApplicationDoesNotExistError,
)
from app.domain.application_answers.dto import AnswerDTO
from app.domain.application_answers.entities import ApplicationAnswer

from .abstract import Repository


class ApplicationRepository(Repository[Application]):
    """Репозиторий для работы с заявками."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=Application, session=session)

    async def create(self, user_id: int) -> ApplicationEntity:
        """Создание заявки."""
        application = Application(user_id=user_id)
        try:
            self.session.add(application)
            await self.session.flush()
        except IntegrityError as e:
            raise ApplicationAlreadyExistsError from e

        application_dto = ApplicationDTO.model_validate(application)
        return ApplicationEntity(data=application_dto)

    async def get_by_id(self, application_id: int) -> ApplicationEntity:
        """Get application by id."""
        stmt = (
            select(Application)
            .options(selectinload(Application.answers))
            .filter_by(id=application_id)
        )
        res = (await self.session.execute(stmt)).scalar_one()
        return self._get_application_entity(res)

    async def retrieve_last(self, user_id: int) -> ApplicationEntity:
        """Retrieve last user application."""
        stmt = (
            select(Application)
            .options(selectinload(Application.answers))
            .where(Application.user_id == user_id)
            .order_by(
                Application.created_at.desc(),
            )
            .limit(1)
        )
        try:
            application = (await self.session.execute(stmt)).scalar_one()
        except NoResultFound as e:
            raise ApplicationDoesNotExistError from e
        return self._get_application_entity(application)

    async def update(self, application: ApplicationEntity) -> ApplicationEntity:
        """Update application."""
        query = (
            update(Application)
            .filter_by(id=application.id)
            .values(
                invite_link=application.invite_link,
                decision_date=application.decision_date,
                rejection_reason=application.rejection_reason,
                status=application.status,
            )
        )
        await self.session.execute(query)

        return application

    async def delete_answers(self, application_id: int) -> None:
        """Удаление всех ответов для заявки."""
        query = delete(ApplicationAnswer).filter_by(
            application_id=application_id,
        )
        await self.session.execute(query)

    def _get_application_entity(self, application: Application) -> ApplicationEntity:
        application_dto = ApplicationDTO.model_validate(application)
        return ApplicationEntity(
            data=application_dto,
            answers={
                a.question_number: ApplicationAnswer(
                    data=AnswerDTO(
                        application_id=a.application_id,
                        answer_text=a.answer_text,
                        question_number=a.question_number,
                    ),
                )
                for a in application.answers
            },
        )
