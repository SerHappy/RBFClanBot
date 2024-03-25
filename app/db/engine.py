from db.repositories import ApplicationAnswerRepository
from db.repositories import ApplicationRepository
from db.repositories import ApplicationStatusRepository
from db.repositories import UserRepository
from decouple import config
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine


def _create_db_engine() -> AsyncEngine:
    """
    Создание подключения к базе данных.

    Args:
        None

    Returns:
        AsyncEngine: Подключение к базе данных.
    """
    return create_async_engine(config("DATABASE_URL"), echo=config("ECHO_DB", cast=bool, default=False))


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
