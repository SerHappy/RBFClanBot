from core.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .repositories import ApplicationRepository
from .repositories.application_answer import ApplicationAnswerRepository
from .repositories.user import UserRepository


def _create_db_engine() -> AsyncEngine:
    """
    Создание подключения к базе данных.

    Args:
        None

    Returns:
        AsyncEngine: Подключение к базе данных.
    """
    return create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        echo=settings.SQLALCHEMY_ECHO,
    )


session_factory: async_sessionmaker = async_sessionmaker(_create_db_engine())


class UnitOfWork:
    def __init__(self) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> None:
        self.session: AsyncSession = self.session_factory()

        self.application = ApplicationRepository(self.session)
        self.application_answer = ApplicationAnswerRepository(self.session)
        self.user = UserRepository(self.session)

    async def __aexit__(self, *args) -> None:
        await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
