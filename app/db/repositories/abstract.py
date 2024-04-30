from typing import Generic, TypeVar

from models import Base
from sqlalchemy.ext.asyncio import AsyncSession

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
