from loguru import logger

from app.db.engine import UnitOfWork
from app.domain.admin_processing_application.dto import AdminProcessingApplicationDTO
from app.domain.admin_processing_application.entities import AdminProcessingApplication
from app.domain.admin_processing_application.exceptions import (
    AdminAlreadyProcessedApplicationError,
)
from app.domain.application.exceptions import ApplicationWrongStatusError
from app.domain.application.value_objects import ApplicationStatusEnum


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

        Returns:
            AdminProcessingApplication: The admin processing application.
        """
        async with self._uow():
            application = await self._uow.application.get_by_id(application_id)
            if application.status != ApplicationStatusEnum.WAITING:
                logger.error(
                    (
                        f"Попытка взять в обработку заявку {application_id=} "
                        f"с неверным статусом {application.status=}"
                    ),
                )
                raise ApplicationWrongStatusError
            admin_processing_application = (
                await self._uow.admin_processing_application.get_by_admin_id(
                    admin_id,
                )
            )
            if admin_processing_application:
                logger.error(
                    (
                        f"Попытка взять в обработку заявку {application_id=} "
                        f"админом {admin_id=}, который уже обрабатывает заявку"
                    ),
                )
                raise AdminAlreadyProcessedApplicationError
            application.take(admin_id)
            await self._uow.application.update(application)
            admin_application = AdminProcessingApplication(
                data=AdminProcessingApplicationDTO(
                    admin_id=admin_id,
                    application_id=application_id,
                ),
            )
            admin_processing_application = (
                await self._uow.admin_processing_application.create(admin_application)
            )
            await self._uow.commit()
            return admin_processing_application
