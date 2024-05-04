import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from _pytest.fixtures import SubRequest
from sqlalchemy import URL
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.domain.application.dto import ApplicationDTO
from app.domain.application.entities import Application
from app.domain.application.value_objects import ApplicationStatusEnum
from app.domain.application_answers.dto import AnswerDTO
from app.domain.application_answers.entities import ApplicationAnswer
from app.domain.user.dto import UserDTO
from app.domain.user.entities import User
from tests import utils


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def database() -> AsyncGenerator[URL, Any]:
    url = make_url(str(settings.SQLALCHEMY_DATABASE_URI) + "_test")
    await utils.create_database(url)

    engine = utils.create_test_db_engine()
    async with engine.begin() as conn:
        await conn.run_sync(utils.apply_migrations)
    await engine.dispose()

    try:
        yield url
    finally:
        await utils.drop_database(url)


@pytest.fixture(scope="session")
async def sqla_engine(database: URL) -> AsyncGenerator[AsyncEngine, Any]:
    engine = create_async_engine(database)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture()
async def session_factory(
    sqla_engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], Any]:
    connection = await sqla_engine.connect()
    trans = await connection.begin()

    try:
        yield async_sessionmaker(
            connection,
            expire_on_commit=False,
            class_=AsyncSession,
            join_transaction_mode="create_savepoint",
        )
    finally:
        await trans.rollback()
        await connection.close()


@pytest.fixture()
def user(request: SubRequest) -> User:
    extra_data = getattr(request, "param", {})
    return User(
        data=UserDTO(
            id=1,
            username="@username",
            first_name="name",
            last_name="lastname",
            is_banned=extra_data.get("is_banned", False),
        ),
    )


@pytest.fixture()
def application(request: SubRequest) -> Application:
    extra_data = getattr(request, "param", {})
    return Application(
        data=ApplicationDTO(
            id=1,
            user_id=1,
            status=extra_data.get("status", ApplicationStatusEnum.IN_PROGRESS),
        ),
        answers=None,
    )


@pytest.fixture()
def answer(application: Application) -> ApplicationAnswer:
    return ApplicationAnswer(
        AnswerDTO(
            application_id=application.id,
            question_number=1,
            answer_text="answer",
        ),
    )
