from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

AbstractModel = TypeVar("AbstractModel", bound=Base)


class Repository(Generic[AbstractModel]):
    """Abstract repository for interacting with the database."""

    model: type[AbstractModel]
    session: AsyncSession

    def __init__(self, type_model: type[AbstractModel], session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            type_model (type[AbstractModel]): The model type.
            session (AsyncSession): The database session.

        Returns:
            None
        """
        self.model = type_model
        self.session = session
