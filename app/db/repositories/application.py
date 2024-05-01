from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repositories.abstract import Repository
from app.domain.application.dto import ApplicationDTO
from app.domain.application.entities import Application as ApplicationEntity
from app.domain.application.exceptions import (
    ApplicationAlreadyExistsError,
    ApplicationDoesNotExistError,
)
from app.domain.application_answers.dto import AnswerDTO
from app.domain.application_answers.entities import ApplicationAnswer
from app.models import Application
from app.models import ApplicationAnswer as ApplicationAnswerModel


class ApplicationRepository(Repository[Application]):
    """
    Responsible for working with the database.

    Manages operations on Application objects.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            session (AsyncSession): The database session.

        Returns:
            None
        """
        super().__init__(type_model=Application, session=session)

    async def create(self, user_id: int) -> ApplicationEntity:
        """
        Create new user application.

        Args:
            user_id (int): The user id.

        Returns:
            ApplicationEntity: The created application.
        """
        application = Application(user_id=user_id)
        try:
            self.session.add(application)
            await self.session.flush()
        except IntegrityError as e:
            raise ApplicationAlreadyExistsError from e

        application_dto = ApplicationDTO.model_validate(application)
        return ApplicationEntity(data=application_dto)

    async def get_by_id(self, application_id: int) -> ApplicationEntity:
        """
        Retrieve application by given id.

        Args:
            application_id (int): The id of the application.

        Returns:
            ApplicationEntity: The application.
        """
        stmt = (
            select(Application)
            .options(selectinload(Application.answers))
            .filter_by(id=application_id)
        )
        try:
            res = (await self.session.execute(stmt)).scalar_one()
        except NoResultFound as e:
            raise ApplicationDoesNotExistError from e
        return self._get_application_entity(res)

    async def retrieve_last(self, user_id: int) -> ApplicationEntity:
        """
        Retrieve last user application.

        Args:
            user_id (int): The user id.

        Raises:
            ApplicationDoesNotExistError: If the application does not exist.

        Returns:
            ApplicationEntity: The application.
        """
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
        """
        Update application in the database.

        Args:
            application (ApplicationEntity): The application to update.

        Returns:
            ApplicationEntity: The updated application.
        """
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
        """
        Delete all answers of application based on the provided application ID.

        Args:
            application_id (int): The application ID.

        Returns:
            None
        """
        query = delete(ApplicationAnswerModel).filter_by(
            application_id=application_id,
        )
        await self.session.execute(query)

    def _get_application_entity(self, application: Application) -> ApplicationEntity:
        """
        Convert application model to application entity.

        Args:
            application (Application): The application model.

        Returns:
            ApplicationEntity: The application entity.
        """
        application_dto = ApplicationDTO.model_validate(application)
        return ApplicationEntity(
            data=application_dto,
            answers={
                a.question_number: ApplicationAnswer(
                    data=AnswerDTO.model_validate(a),
                )
                for a in application.answers
            },
        )
