from app.db.engine import UnitOfWork
from app.domain.user.entities import User


class UserBanService:
    """Responsible for user ban."""

    def __init__(self, uow: UnitOfWork) -> None:
        """
        Initialize the service instance.

        Args:
            uow (UnitOfWork): The unit of work instance.

        Returns:
            None
        """
        self._uow = uow

    async def execute(self, user_id: int) -> User:
        """
        Execute the service.

        Args:
            user_id (int): Telegram ID of the user.

        Raises:
            UserNotFoundError: If the user is not found.
            UserIsBannedError: If the user is already banned.

        Returns:
            User: Banned user.
        """
        async with self._uow():
            user = await self._uow.user.retrieve(user_id)
            user.ban()
            await self._uow.user.update(user)
            await self._uow.commit()
        return user
