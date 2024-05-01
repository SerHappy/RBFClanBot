from app.db.engine import UnitOfWork
from app.domain.application.entities import Application


class ApplicationCompleteService:
    """Responsible for application answer update."""

    def __init__(self, uow: UnitOfWork) -> None:
        """
        Initialize the service instance.

        Args:
            uow (UnitOfWork): The unit of work instance.

        Returns:
            None
        """
        self._uow = uow

    async def execute(self, user_id: int) -> Application:
        """
        Execute the service.

        Args:
            user_id (int): Telegram ID of the user.

        Raises:
            ApplicationDoesNotExistError: If the application does not exist.
            ApplicationDoesNotCompeteError: If the application does not complete.
            ChangeApplicationStatusError: If the current status is wrong.

        Returns:
            Application: Completed application.
        """
        async with self._uow():
            user_application = await self._uow.application.retrieve_last(user_id)
            user_application.complete()
            await self._uow.application.update(user_application)
            await self._uow.commit()
            return user_application
