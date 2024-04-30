from app.db.engine import UnitOfWork
from app.domain.user.entities import User
from app.domain.user.exceptions import UserNotFoundError


class UserUnbanService:
    """Responsible for user unban."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize the service instance."""
        self._uow = uow

    async def execute(self, user_id: int) -> User:
        """Execute the service."""
        async with self._uow():
            user = await self._uow.user.retrieve(user_id)
            if not user:
                raise UserNotFoundError
            user.unban()
            await self._uow.user.update(user)
            await self._uow.commit()
        return user
