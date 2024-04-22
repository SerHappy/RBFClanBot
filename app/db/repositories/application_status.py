from models import ApplicationStatus
from sqlalchemy.ext.asyncio import AsyncSession

from .abstract import Repository


class ApplicationStatusRepository(Repository[ApplicationStatus]):
    """Репозиторий для работы с статусами заявок."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=ApplicationStatus, session=session)

    async def create(self, status: str) -> ApplicationStatus:
        """
        Создание статуса заявки.

        Args:
            status: Статус заявки.

        Returns:
            Экземпляр ApplicationStatus (созданный).
        """
        new_status = await self.session.merge(self.model(status=status))
        return new_status
