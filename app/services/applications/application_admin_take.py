from loguru import logger

from app.db.engine import UnitOfWork
from app.domain.admin_processing_application.dto import AdminProcessingApplicationDTO
from app.domain.admin_processing_application.entities import AdminProcessingApplication
from app.domain.admin_processing_application.exceptions import (
    AdminAlreadyProcessedApplicationError,
    AdminProcessingApplicationDoesNotExistError,
)


class ApplicationAdminTakeService:
    """Represents an application admin take service."""

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
        admin_id: int,
        application_id: int,
    ) -> AdminProcessingApplication:
        """
        Execute the service.

        Args:
            admin_id (int): Telegram ID of the admin.
            application_id (int): Telegram ID of the application.

        Raises:
            ApplicationDoesNotExistError: If the application does not exist.
            AdminAlreadyProcessedApplicationError: If the admin already processed
            the application.
            ChangeApplicationStatusError: If the current status is wrong.

        Returns:
            AdminProcessingApplication: The admin processing application.
        """
        async with self._uow():
            application = await self._uow.application.get_by_id(application_id)
            try:
                admin_processing_application = (
                    await self._uow.admin_processing_application.get_by_admin_id(
                        admin_id,
                    )
                )
                logger.error(
                    (
                        f"Попытка взять в обработку заявку {application_id=} "
                        f"админом {admin_id=}, который уже обрабатывает заявку"
                    ),
                )
                raise AdminAlreadyProcessedApplicationError
            except AdminProcessingApplicationDoesNotExistError:
                application.take(admin_id)
                await self._uow.application.update(application)
                admin_application = AdminProcessingApplication(
                    data=AdminProcessingApplicationDTO(
                        admin_id=admin_id,
                        application_id=application_id,
                    ),
                )
                admin_processing_application = (
                    await self._uow.admin_processing_application.create(
                        admin_application,
                    )
                )
                await self._uow.commit()
                return admin_processing_application
