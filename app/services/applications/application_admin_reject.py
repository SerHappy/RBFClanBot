from db.engine import UnitOfWork
from loguru import logger

from app.domain.admin_processing_application.exceptions import (
    ApplicationAlreadyProcessedError,
    WrongAdminError,
)
from app.domain.application.entities import Application
from app.domain.application.exceptions import ApplicationWrongStatusError
from app.domain.application.value_objects import ApplicationStatusEnum


class ApplicationAdminRejectService:
    """Represents an application reject service."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize the service instance."""
        self._uow = uow

    async def execute(
        self,
        admin_id: int,
        application_id: int,
        rejection_reason: str,
    ) -> Application:
        """Reject an application."""
        async with self._uow():
            admin_application = (
                await self._uow.admin_processing_application.get_by_admin_id(admin_id)
            )
            if admin_application is None:
                raise ApplicationAlreadyProcessedError
            if admin_application.application_id != application_id:
                logger.error(
                    "Попытка отклонить заявку с неверным админом.",
                )
                raise WrongAdminError
            application = await self._uow.application.get_by_id(application_id)
            if application.status != ApplicationStatusEnum.PROCESSING:
                logger.error("Попытка отклонить заявку с неверным статусом.")
                raise ApplicationWrongStatusError
            application.reject(rejection_reason)
            await self._uow.application.update(application)
            await self._uow.admin_processing_application.delete(admin_application)
            await self._uow.commit()
            return application
