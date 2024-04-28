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
        """Создание пользователя.

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

    async def update_ban_status(self, user: UserEntity) -> UserEntity:
        """Update user ban status."""
        query = (
            update(self.model).filter_by(id=user.id).values(is_banned=user.is_banned)
        )
        await self.session.execute(query)

        return user

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        """Get user by id."""
        stmt = select(self.model).filter_by(id=user_id)

        res = (await self.session.execute(stmt)).scalar_one_or_none()

        if res is None:
            return None

        user_dto = UserDTO(
            id=res.id,
            username=res.username,
            first_name=res.first_name,
            last_name=res.last_name,
            is_banned=res.is_banned,
        )
        return UserEntity(user_dto)

    async def is_user_banned(self, user_id: int) -> bool:
        """Проверка забанен ли пользователь."""
        user = await self.get(user_id)
        if not user:
            logger.error(f"Пользователь с id={user_id} не найден при проверке бана.")
            return False
        return user.is_banned

    async def ban_user(self, user_id: int):
        """Забанить пользователя."""
        user = await self.get(user_id)
        if not user:
            logger.error(f"Пользователь с id={user_id} не найден при попытке бане.")
            return
        await self.session.execute(
            update(UserModel).where(UserModel.id == user_id).values(is_banned=True),
        )
        logger.info(f"Пользователь id={user_id} был забанен.")

    async def unban_user(self, user_id: int):
        """Разбанить пользователя."""
        user = await self.get(user_id)
        if not user:
            logger.error(f"Пользователь с id={user_id} не найден при попытке разбана.")
            return
        await self.session.execute(
            update(UserModel).where(UserModel.id == user_id).values(is_banned=False),
        )
        logger.info(f"Пользователь id={user_id} был разбанен.")
