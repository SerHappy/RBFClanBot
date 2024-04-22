from core.config import settings
from db.repositories import (
    AdminProcessingApplicationRepository,
    ApplicationAnswerRepository,
    ApplicationRepository,
    ApplicationStatusRepository,
    UserRepository,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


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


Session: async_sessionmaker = async_sessionmaker(_create_db_engine())


class Database:
    """
    Класс для работы с базой данных.

    Хранит репозитории для работы с пользователями, заявками, ответами, статусами заявок.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозиториев."""
        self._session = session
        self.user = UserRepository(session)
        self.application = ApplicationRepository(session)
        self.application_answer = ApplicationAnswerRepository(session)
        self.application_status = ApplicationStatusRepository(session)
        self.admin_processing_application = AdminProcessingApplicationRepository(
            session
        )
