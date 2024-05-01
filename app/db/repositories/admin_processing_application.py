from loguru import logger
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.abstract import Repository
from app.domain.admin_processing_application.dto import AdminProcessingApplicationDTO
from app.domain.admin_processing_application.entities import (
    AdminProcessingApplication as AdminProcessingApplicationEntity,
)
from app.domain.admin_processing_application.exceptions import (
    ApplicationAlreadyProcessedError,
)
from app.models import AdminProcessingApplication


class AdminProcessingApplicationRepository(Repository[AdminProcessingApplication]):
    """
    Responsible for working with the database.

    Manages operations on AdminProcessingApplication objects.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            session (AsyncSession): The database session.

        Returns:
            None
        """
        super().__init__(type_model=AdminProcessingApplication, session=session)

    async def create(
        self,
        entity: AdminProcessingApplicationEntity,
    ) -> AdminProcessingApplicationEntity:
        """
        Insert a new AdminProcessingApplicationEntity into the database.

        Args:
            entity (AdminProcessingApplicationEntity): The entity to insert.

        Returns:
            AdminProcessingApplicationEntity: The inserted entity.
        """
        query = insert(self.model).values(
            admin_id=entity.admin_id,
            application_id=entity.application_id,
        )
        try:
            await self.session.execute(query)
        except IntegrityError as e:
            raise ApplicationAlreadyProcessedError from e
        return entity

    async def get_by_admin_id(
        self,
        admin_id: int,
    ) -> AdminProcessingApplicationEntity | None:
        """
        Retrieve an AdminProcessingApplicationEntity by given admin_id.

        Args:
            admin_id (int): The id of the admin.

        Returns:
            AdminProcessingApplicationEntity | None: The entity if found, else None.
        """
        logger.debug(f"Получение обрабатываемой админом {admin_id=} заявки")
        query = select(self.model).filter_by(admin_id=admin_id)
        res = (await self.session.execute(query)).scalar_one_or_none()
        # TODO: Raise does not exist
        if not res:
            return None
        return self._get_entity(res)

    async def delete(self, entity: AdminProcessingApplicationEntity) -> None:
        """
        Delete an AdminProcessingApplicationEntity from the database.

        Args:
            entity (AdminProcessingApplicationEntity): The entity to delete.

        Returns:
            None
        """
        query = delete(self.model).filter_by(
            admin_id=entity.admin_id,
            application_id=entity.application_id,
        )
        await self.session.execute(query)

    def _get_entity(
        self,
        obj: AdminProcessingApplication,
    ) -> AdminProcessingApplicationEntity:
        """
        Convert an database object to an AdminProcessingApplicationEntity.

        Args:
            obj (AdminProcessingApplication): The object to convert.

        Returns:
            AdminProcessingApplicationEntity: The converted entity.
        """
        return AdminProcessingApplicationEntity(
            data=AdminProcessingApplicationDTO.model_validate(obj),
        )
