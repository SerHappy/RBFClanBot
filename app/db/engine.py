from db.repositories import ApplicationAnswerRepository
from db.repositories import ApplicationRepository
from db.repositories import UserRepository
from decouple import config
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine


def create_db_engine() -> AsyncEngine:
    """Create database engine."""
    return create_async_engine(config("DATABASE_URL"), echo=True)


Session = async_sessionmaker(create_db_engine())


class Database:
    """Base class to manipulate database."""

    user: UserRepository

    def __init__(self, session: AsyncSession) -> None:
        """Initialize database."""
        self._session = session
        self.user = UserRepository(session)
        self.application = ApplicationRepository(session)
        self.application_answer = ApplicationAnswerRepository(session)
