import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
async def uow(session_factory: async_sessionmaker[AsyncSession]) -> TestUnitOfWork:
    return TestUnitOfWork(session_factory)
