from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.engine import UnitOfWork


class TestUnitOfWork(UnitOfWork):
    __test__ = False

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
