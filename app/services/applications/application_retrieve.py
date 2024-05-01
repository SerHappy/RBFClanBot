from app.db.engine import UnitOfWork
from app.domain.application.entities import Application


class ApplicationRetrieveService:
    """Responsible for application retrieval."""

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

        Returns:
            Application: Retrieved application.
        """
        async with self._uow():
            return await self._uow.application.retrieve_last(user_id)
