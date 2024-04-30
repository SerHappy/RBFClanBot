from loguru import logger

from app.db.engine import UnitOfWork
from app.domain.admin_processing_application.exceptions import (
    ApplicationAlreadyProcessedError,
    WrongAdminError,
)
from app.domain.application.entities import Application
from app.domain.application.exceptions import ApplicationWrongStatusError
from app.domain.application.value_objects import ApplicationStatusEnum


class ApplicationAdminAcceptService:
    """Represents an application accept service."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize the service instance."""
        self._uow = uow

    async def execute(
        self,
        admin_id: int,
        application_id: int,
        invite_link: str,
    ) -> Application:
        """Accept an application."""
        async with self._uow():
            admin_application = (
                await self._uow.admin_processing_application.get_by_admin_id(admin_id)
            )
            if admin_application is None:
                raise ApplicationAlreadyProcessedError
            if admin_application.application_id != application_id:
                logger.error(
                    "Попытка принять заявку с неверным админом.",
                )
                raise WrongAdminError
            application = await self._uow.application.get_by_id(application_id)
            if application.status != ApplicationStatusEnum.PROCESSING:
                logger.error("Попытка принять заявку с неверным статусом.")
                raise ApplicationWrongStatusError
            application.accept(invite_link)
            await self._uow.application.update(application)
            await self._uow.admin_processing_application.delete(admin_application)
            await self._uow.commit()
            return application
