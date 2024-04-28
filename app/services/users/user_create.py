from loguru import logger

from app.db.engine import UnitOfWork
from app.domain.user.dto import UserDTO
from app.domain.user.entities import User
from app.domain.user.exceptions import UserAlreadyExistsError
from app.services.users.dto import UserCreateDTO


class EnsureUserExistsService:
    """Service for ensuring that the user exists."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize the service instance."""
        self._uow = uow

    async def execute(self, data: UserCreateDTO) -> User:
        """Get or create the user."""
        user = await self._get_user(data.id)
        if not user:
            user_dto = UserDTO(
                id=data.id,
                username=data.username,
                first_name=data.first_name,
                last_name=data.last_name,
            )
            user = await self._create_user(user_dto)
        return user

    async def _get_user(self, user_id: int) -> User | None:
        async with self._uow():
            return await self._uow.user.get_by_id(user_id)

    async def _create_user(self, data: UserDTO) -> User:
        async with self._uow():
            user = User(data=data)
            try:
                user = await self._uow.user.create(user)
                await self._uow.commit()
            except UserAlreadyExistsError:
                logger.info(f"User with id {data.id} already exists.")
        return user
