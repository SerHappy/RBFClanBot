from datetime import datetime

from loguru import logger
from models import Application
from sqlalchemy import select, update
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

        application_dto = ApplicationDTO(
            id=application.id,
            user_id=application.user_id,
            status=application.status,
        )
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

    async def retrieve_all(
        self,
        user_id: int,
    ) -> list[ApplicationEntity]:
        """Retrieve user applications."""
        stmt = (
            select(Application)
            .options(selectinload(Application.answers))
            .where(Application.user_id == user_id)
            .order_by(
                Application.decision_date.desc(),
            )
        )
        res = (await self.session.execute(stmt)).scalars().all()
        return [self._get_application_entity(application) for application in res]

    async def retrieve_last(self, user_id: int) -> ApplicationEntity:
        """Retrieve last user application."""
        stmt = (
            select(Application)
            .options(selectinload(Application.answers))
            .where(Application.user_id == user_id)
            .order_by(
                Application.decision_date.desc(),
            )
            .limit(1)
        )
        try:
            application = (await self.session.execute(stmt)).scalar_one()
        except NoResultFound as e:
            raise ApplicationDoesNotExistError from e
        return self._get_application_entity(application)

    async def get_active_application(self, user_id: int) -> Application | None:
        """Получить активную заявку пользователя.

        Args:
        ----
            user_id: ID пользователя.

        Returns:
        -------
            Заявка пользователя Application или None.

        """
        logger.debug(f"Получение активной заявки пользователя с id={user_id}")
        statement = (
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.decision_date.desc())
            .limit(1)
        )
        res = (await self.session.execute(statement)).scalar()
        if res is None:
            logger.debug(f"Не найдена активная заявка пользователя с id={user_id}")
            return None
        logger.debug(f"Найдена активная заявка пользователя с id={user_id}")
        return res

    async def add_link(
        self,
        application: ApplicationEntity,
    ) -> ApplicationEntity:
        """Add link to application."""
        query = (
            update(Application)
            .filter_by(id=application.id)
            .values(invite_link=application.invite_link)
        )
        await self.session.execute(query)

        return application

    async def add_reject_reason(
        self,
        application: ApplicationEntity,
    ) -> ApplicationEntity:
        """Add reject reason to application."""
        query = (
            update(Application)
            .filter_by(id=application.id)
            .values(rejection_reason=application.rejection_reason)
        )
        await self.session.execute(query)

        return application

    async def add_decision_date(
        self,
        application: ApplicationEntity,
    ) -> ApplicationEntity:
        """Add reject reason to application."""
        query = (
            update(Application)
            .filter_by(id=application.id)
            .values(decision_date=application.decision_date)
        )
        await self.session.execute(query)

        return application

    # TODO: Create one update method to update all fields
    async def update_status(self, application: ApplicationEntity) -> ApplicationEntity:
        """Update application status."""
        query = (
            update(Application)
            .filter_by(id=application.id)
            .values(status=application.status)
        )
        await self.session.execute(query)

        return application

    async def change_status(self, application_id: int, status_id: int) -> None:
        """Смена статуса заявки.

        Args:
        ----
            application_id: ID заявки.
            status_id: ID статуса.

        Returns:
        -------
            None

        """
        logger.debug(
            f"Смена статуса заявки application_id={application_id} на status_id={status_id}",
        )
        statement = (
            update(Application)
            .where(Application.id == application_id)
            .values(status_id=status_id)
        )
        await self.session.execute(statement)
        logger.debug(
            f"Статус заявки application_id={application_id} изменен на status_id={status_id}",
        )

    async def approve_application(self, application_id: int, invite_link: str) -> None:
        """Принятие заявки.

        Перевод статуса заявки в 3 и добавление ссылки на приглашение.

        Args:
        ----
            application_id: ID заявки.
            invite_link: Ссылка на приглашение.

        Returns:
        -------
            None

        """
        logger.debug(
            f"Принятие заявки application_id={application_id}, перевод в статус 3 и добавление ссылки invite_link={invite_link}",
        )
        await self.change_status(application_id, 3)
        statement = (
            update(Application)
            .where(Application.id == application_id)
            .values(decision_date=datetime.now(), invite_link=invite_link)
        )
        await self.session.execute(statement)
        logger.debug(f"Заявка application_id={application_id} принята")

    async def reject_application(
        self,
        application_id: int,
        rejection_reason: str,
    ) -> None:
        """Отклонение заявки.

        Перевод статуса заявки в 4 и добавление причины отклонения.

        Args:
        ----
            application_id: ID заявки.
            rejection_reason: Причина отклонения.

        Returns:
        -------
            None

        """
        logger.debug(
            f"Отклонение заявки application_id={application_id}, перевод в статус 4 и добавление причины rejection_reason={rejection_reason}",
        )
        await self.change_status(application_id, 4)
        statement = (
            update(Application)
            .where(Application.id == application_id)
            .values(decision_date=datetime.now(), rejection_reason=rejection_reason)
        )
        await self.session.execute(statement)
        logger.debug(f"Заявка application_id={application_id} отклонена")

    def _get_application_entity(self, application: Application) -> ApplicationEntity:
        application_dto = ApplicationDTO(
            id=application.id,
            user_id=application.user_id,
            status=application.status,
            decision_date=application.decision_date,
            rejection_reason=application.rejection_reason,
            invite_link=application.invite_link,
        )
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
