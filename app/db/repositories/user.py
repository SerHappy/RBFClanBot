from loguru import logger
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.abstract import Repository
from app.domain.user.dto import UserDTO
from app.domain.user.entities import User as UserEntity
from app.domain.user.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.models import User as UserModel


class UserRepository(Repository[UserModel]):
    """
    Responsible for working with the database.

    Manages operations on User objects.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            session (AsyncSession): The database session.

        Returns:
            None
        """
        super().__init__(type_model=UserModel, session=session)

    async def create(self, user: UserEntity) -> UserEntity:
        """
        Create new user in the database.

        Args:
            user (UserEntity): The user entity instance.

        Returns:
            UserEntity: The created user.
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
            user (UserEntity): The user to update.

        Returns:
            UserEntity: The updated user.
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
            user_id (int): Telegram ID of the user.

        Returns:
            UserEntity: The user.

        """
        stmt = select(self.model).filter_by(id=user_id)
        try:
            res = (await self.session.execute(stmt)).scalar_one()
        except NoResultFound as e:
            raise UserNotFoundError from e

        return self._get_user(res)

    def _get_user(self, obj: UserModel) -> UserEntity:
        """
        Convert database object to UserEntity.

        Args:
            obj (UserModel): The object to convert.

        Returns:
            UserEntity: The converted user.
        """
        data = UserDTO.model_validate(obj)
        return UserEntity(data)
