from models import Base
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from typing import Generic
from typing import Type
from typing import TypeVar

import abc


AbstractModel = TypeVar("AbstractModel")


class Repository(Generic[AbstractModel]):
    """Abstract repository."""

    type_model: Type[Base]
    session: AsyncSession

    def __init__(self, type_model: Type[Base], session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            type_model: Model.
            session: Session.
        """
        self.type_model = type_model
        self.session = session

    async def get(self, pk: int | str) -> AbstractModel | None:
        """Get model by pk.

        Args:
            pk: Identifier.

        Returns:
            Model.
        """
        return await self.session.get(self.type_model, ident=pk)

    async def get_by_where(self, where_clause: Any) -> AbstractModel | None:
        """Get one model by where clause.

        Args:
            where_clause: Where clause.

        Returns:
            Model or None.
        """
        statement = select(self.type_model).where(where_clause)
        return (await self.session.execute(statement)).one_or_none()  # type: ignore

    async def get_many(self, where_clause: Any, limit: int = 100, order_by: Any = None) -> list[AbstractModel]:
        """Get many models by where clause.

        Args:
            where_clause: Where clause.

        Returns:
            Models.
        """
        statement = select(self.type_model).where(where_clause).limit(limit)
        if order_by:
            statement = statement.order_by(order_by)
        return (await self.session.execute(statement)).all()  # type: ignore

    async def delete(self, where_clause: Any) -> None:
        """Delete model.

        Args:
            model: Model.
        """
        statement = delete(self.type_model).where(where_clause)
        await self.session.execute(statement)

    @abc.abstractmethod
    async def create(self, *args, **kwargs) -> None:
        """Create model. Should be implemented in subclasses."""
        pass
