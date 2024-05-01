from loguru import logger

from app.db.engine import UnitOfWork
from app.domain.admin_processing_application.exceptions import (
    AdminProcessingApplicationDoesNotExistError,
    ApplicationAlreadyProcessedError,
    WrongAdminError,
)
from app.domain.application.entities import Application


class ApplicationAdminAcceptService:
    """Represents an application accept service."""

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
        invite_link: str,
    ) -> Application:
        """
        Accept an application.

        Args:
            admin_id (int): Telegram ID of the admin.
            application_id (int): Telegram ID of the application.
            invite_link (str): The invite link.

        Raises:
            ApplicationAlreadyProcessedError: If the application is already processed.
            WrongAdminError: If the admin is not the same as the application.
            ChangeApplicationStatusError: If the current status is wrong.

        Returns:
            Application: The accepted application.
        """
        async with self._uow():
            try:
                admin_application = (
                    await self._uow.admin_processing_application.get_by_admin_id(
                        admin_id,
                    )
                )
            except AdminProcessingApplicationDoesNotExistError as e:
                raise ApplicationAlreadyProcessedError from e
            if admin_application.application_id != application_id:
                logger.error(
                    "Попытка принять заявку с неверным админом.",
                )
                raise WrongAdminError
            application = await self._uow.application.get_by_id(application_id)
            application.accept(invite_link)
            await self._uow.application.update(application)
            await self._uow.admin_processing_application.delete(admin_application)
            await self._uow.commit()
            return application
