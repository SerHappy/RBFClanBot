import abc
from typing import Any, Generic, Type, TypeVar

from models import Base
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

AbstractModel = TypeVar("AbstractModel", bound=Base)


class Repository(Generic[AbstractModel]):
    """Abstract repository."""

    model: Type[AbstractModel]
    session: AsyncSession

    def __init__(self, type_model: Type[AbstractModel], session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            type_model: Model.
            session: Session.
        """
        self.model = type_model
        self.session = session

    async def get(self, pk: int | str) -> AbstractModel | None:
        """Get model by pk.

        Args:
            pk: Identifier.

        Returns:
            Model.
        """
        return await self.session.get(self.model, ident=pk)

    async def get_by_where(self, where_clause: Any) -> AbstractModel | None:
        """Get one model by where clause.

        Args:
            where_clause: Where clause.

        Returns:
            Model or None.
        """
        statement = select(self.model).where(where_clause)
        return (await self.session.execute(statement)).one_or_none()  # type: ignore

    async def get_many(
        self, where_clause: Any, limit: int = 100, order_by: Any = None
    ) -> list[AbstractModel]:
        """Get many models by where clause.

        Args:
            where_clause: Where clause.

        Returns:
            Models.
        """
        statement = select(self.model).where(where_clause).limit(limit)
        if order_by:
            statement = statement.order_by(order_by)
        return (await self.session.execute(statement)).all()  # type: ignore

    async def delete(self, where_clause: Any) -> None:
        """Delete model.

        Args:
            model: Model.
        """
        statement = delete(self.model).where(where_clause)
        await self.session.execute(statement)

    @abc.abstractmethod
    async def create(self, *args, **kwargs) -> None:
        """Create model. Should be implemented in subclasses."""
        pass
