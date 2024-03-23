from .abstract import Repository
from models import ApplicationStatus
from sqlalchemy.ext.asyncio import AsyncSession


class ApplicationStatusRepository(Repository[ApplicationStatus]):
    """Application status repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize Application status repository."""
        super().__init__(type_model=ApplicationStatus, session=session)

    async def create(self, status: str) -> ApplicationStatus:
        """Create new Application status.

        Args:
            status: str.

        Returns:
            ApplicationStatus.
        """
        new_status = await self.session.merge(self.type_model(status=status))
        return new_status
