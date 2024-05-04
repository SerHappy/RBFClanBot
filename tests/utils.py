from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from pathlib import Path
from alembic.config import Config
from alembic import command
from sqlalchemy import URL, Connection, NullPool, text
import os

from app.core.config import settings


def create_test_db_engine() -> AsyncEngine:
    """
    Create an asynchronous database engine.

    Returns:
        AsyncEngine: An asynchronous database engine.
    """
    test_database_url = str(settings.SQLALCHEMY_DATABASE_URI) + "_test"
    return create_async_engine(
        test_database_url,
        echo=True,
    )


def apply_migrations(connection: Connection) -> None:
    base_dir = Path(__file__).resolve().parent.parent
    alembic_cfg = Config(base_dir.joinpath("alembic.ini"))

    alembic_cfg.attributes["connection"] = connection
    command.upgrade(alembic_cfg, "head")


async def create_database(url: URL) -> None:
    database_name = url.database
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost/postgres",
        isolation_level="AUTOCOMMIT",
    )
    async with engine.connect() as conn:
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'")
        )
        database_exists = result.scalar() == 1

    if database_exists:
        await drop_database(url)

    async with engine.connect() as conn:
        await conn.execute(
            text(
                f'CREATE DATABASE "{database_name}" ENCODING "utf8" TEMPLATE template1'
            )
        )
    await engine.dispose()


async def drop_database(url: URL) -> None:
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost/postgres",
        isolation_level="AUTOCOMMIT",
    )
    async with engine.connect() as conn:
        disc_users = """
        SELECT pg_terminate_backend(pg_stat_activity.%(pid_column)s)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '%(database)s'
          AND %(pid_column)s <> pg_backend_pid();
        """ % {
            "pid_column": "pid",
            "database": url.database,
        }
        await conn.execute(text(disc_users))

        await conn.execute(text(f'DROP DATABASE "{url.database}"'))
