from loguru import logger
from models import User as UserModel
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.dto import UserDTO
from app.domain.user.entities import User as UserEntity
from app.domain.user.exceptions import UserAlreadyExistsError

from .abstract import Repository


class UserRepository(Repository[UserModel]):
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=UserModel, session=session)

    async def create(self, user: UserEntity) -> UserEntity:
        """
        Создание пользователя.

        Args:
        ----
            user: Пользователь.

        Returns:
        -------
            Экземпляр User (созданный).

        """
        logger.debug(f"Создание пользователя с id={user.id}")
        query = insert(self.model).values(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_banned=user.is_banned,
        )
        try:
            await self.session.execute(query)
        except IntegrityError as e:
            raise UserAlreadyExistsError from e
        logger.debug(f"Создан пользователь с id={user.id}")
        return user

    async def update(self, user: UserEntity) -> UserEntity:
        """
        Update the user data in the database based on the provided user.

        Args:
        ----
            user: The user entity instance containing updated fields that
            need to be persisted in the database.

        Returns:
        -------
            The updated user.

        """
        query = (
            update(self.model)
            .filter_by(id=user.id)
            .values(
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_banned=user.is_banned,
            )
        )
        await self.session.execute(query)

        return user

    async def retrieve(self, user_id: int) -> UserEntity:
        """
        Retrieve the user from database based on the provided Telegram ID.

        Args:
        ----
            user_id: Telegram ID of the user.

        Returns:
        -------
            The user.

        """
        stmt = select(self.model).filter_by(id=user_id)

        res = (await self.session.execute(stmt)).scalar_one()

        return self._get_user(res)

    def _get_user(self, obj: UserModel) -> UserEntity:
        data = UserDTO.model_validate(obj)
        return UserEntity(data)
