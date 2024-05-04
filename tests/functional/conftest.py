import pytest
from tests.environment.unit_of_work import TestUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@pytest.fixture
async def uow(session_factory: async_sessionmaker[AsyncSession]) -> TestUnitOfWork:
    return TestUnitOfWork(session_factory)
