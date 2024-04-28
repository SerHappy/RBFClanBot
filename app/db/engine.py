from types import TracebackType

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.db.repositories import ApplicationRepository
from app.db.repositories.admin_processing_application import (
    AdminProcessingApplicationRepository,
)
from app.db.repositories.application_answer import ApplicationAnswerRepository
from app.db.repositories.user import UserRepository


def _create_db_engine() -> AsyncEngine:
    """Создание подключения к базе данных.

    Args:
    ----
        None

    Returns:
    -------
        AsyncEngine: Подключение к базе данных.

    """
    return create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        echo=settings.SQLALCHEMY_ECHO,
    )


session_factory: async_sessionmaker = async_sessionmaker(_create_db_engine())


class UnitOfWork:
    """Provides a unit of work pattern for managing transactions and repositories."""

    def __init__(self) -> None:
        """Initialize the unit of work instance."""
        self._session_factory = session_factory

    def __call__(self) -> "UnitOfWork":
        """Call the unit of work."""
        return self

    async def __aenter__(self) -> "UnitOfWork":
        """Enter the unit of work.

        Initialize the session and repositories.
        """
        self._session: AsyncSession = self._session_factory()

        self.application = ApplicationRepository(self._session)
        self.application_answer = ApplicationAnswerRepository(self._session)
        self.admin_processing_application = AdminProcessingApplicationRepository(
            self._session,
        )
        self.user = UserRepository(self._session)
        return self

    # TODO: Add exception handling
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the unit of work."""
        await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        """Commit the changes to the database."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the changes to the database."""
        await self._session.rollback()
