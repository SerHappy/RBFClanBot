from .abstract import Repository
from loguru import logger
from models import AdminProcessingApplication
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AdminProcessingApplicationRepository(Repository[AdminProcessingApplication]):
    """Репозиторий для работы с связями админов и обрабатываемых ими заявок."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=AdminProcessingApplication, session=session)

    async def create(self, admin_id: int, application_id: int):
        """Создание связи админа и обрабатываемой им заявки."""
        logger.debug(f"Создание связи админа {admin_id=} и заявки {application_id=}")
        row = await self.session.merge(self.type_model(admin_id=admin_id, application_id=application_id))
        return row

    async def get_admin_processing_application(self, admin_id: int) -> AdminProcessingApplication | None:
        """Получение обрабатываемой админов заявки, если она есть."""
        logger.debug(f"Получение обрабатываемой админом {admin_id=} заявки")
        query = select(self.type_model).where(self.type_model.admin_id == admin_id)
        res = await self.session.execute(query)
        return res.scalar_one_or_none()

    async def delete(self, admin_id: int) -> None:
        """Удаление связи админа и обрабатываемой им заявки."""
        logger.debug(f"Удаление связи админа {admin_id=} и заявки")
        row = await self.get_admin_processing_application(admin_id=admin_id)
        try:
            await self.session.delete(row)
        except Exception as e:
            logger.error(f"Ошибка при удалении связи админа {admin_id=} и заявки: {e}")
