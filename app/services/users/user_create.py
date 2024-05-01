from app.db.engine import UnitOfWork
from app.domain.user.dto import UserDTO
from app.domain.user.entities import User
from app.domain.user.exceptions import UserNotFoundError
from app.services.users.dto import UserCreateDTO


class EnsureUserExistsService:
    """Service for ensuring that the user exists."""

    def __init__(self, uow: UnitOfWork) -> None:
        """
        Initialize the service instance.

        Args:
            uow (UnitOfWork): The unit of work instance.

        Returns:
            None
        """
        self._uow = uow

    async def execute(self, data: UserCreateDTO) -> User:
        """
        Ensure that the user exists.

        Args:
            data (UserCreateDTO): The data of the user.

        Returns:
            User: The retrieved or created user.
        """
        try:
            user = await self._get_user(data.id)
        except UserNotFoundError:
            user_dto = UserDTO(**data.model_dump())
            user = await self._create_user(user_dto)
        return user

    async def _get_user(self, user_id: int) -> User:
        async with self._uow():
            return await self._uow.user.retrieve(user_id)

    async def _create_user(self, data: UserDTO) -> User:
        async with self._uow():
            user = User(data=data)
            user = await self._uow.user.create(user)
            await self._uow.commit()
        return user
