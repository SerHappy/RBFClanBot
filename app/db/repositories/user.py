from .abstract import Repository
from loguru import logger
from models import User
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(Repository[User]):
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=User, session=session)

    async def create(
        self,
        id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Создание пользователя.

        Args:
            id: идентификатор пользователя.
            username: никнейм пользователя (Optional).
            first_name: Имя (Optional).
            last_name: Фамилия (Optional).

        Returns:
            Экземпляр User (созданный).
        """
        logger.debug(f"Создание пользователя с id={id}")
        user = await self.session.merge(
            self.type_model(
                id=id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
        )
        logger.debug(f"Создан пользователь с id={id}")
        return user

    async def create_if_not_exists(
        self,
        id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Создание пользователя в случае его отсутствия.

        Args:
            id: идентификатор пользователя.
            username: никнейм пользователя (Optional).
            first_name: Имя (Optional).
            last_name: Фамилия (Optional).

        Returns:
            Экземпляр User (найденный или созданный).
        """
        logger.debug(f"Создание или получение пользователя с id={id}")
        user = await self.get(id)
        if user is None:
            logger.debug(f"Пользователь с id={id} не существует, создаем")
            user = await self.create(id, username, first_name, last_name)
        return user
