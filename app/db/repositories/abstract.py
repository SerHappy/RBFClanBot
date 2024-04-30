from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

AbstractModel = TypeVar("AbstractModel", bound=Base)


class Repository(Generic[AbstractModel]):
    """Abstract repository."""

    model: type[AbstractModel]
    session: AsyncSession

    def __init__(self, type_model: type[AbstractModel], session: AsyncSession) -> None:
        """
        Initialize repository.

        Args:
        ----
            type_model: Model.
            session: Session.

        """
        self.model = type_model
        self.session = session
