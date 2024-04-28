from loguru import logger
from models import AdminProcessingApplication
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.admin_processing_application.dto import AdminProcessingApplicationDTO
from app.domain.admin_processing_application.entities import (
    AdminProcessingApplication as AdminProcessingApplicationEntity,
)
from app.domain.admin_processing_application.exceptions import (
    ApplicationAlreadyProcessedError,
)

from .abstract import Repository


class AdminProcessingApplicationRepository(Repository[AdminProcessingApplication]):
    """Репозиторий для работы с связями админов и обрабатываемых ими заявок."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=AdminProcessingApplication, session=session)

    async def create(
        self,
        admin_id: int,
        application_id: int,
    ) -> AdminProcessingApplicationEntity:
        """Создание связи админа и обрабатываемой им заявки."""
        admin_processing_application = AdminProcessingApplication(
            admin_id=admin_id,
            application_id=application_id,
        )
        try:
            self.session.add(admin_processing_application)
        except IntegrityError as e:
            raise ApplicationAlreadyProcessedError from e
        return AdminProcessingApplicationEntity(
            data=AdminProcessingApplicationDTO(
                admin_id=admin_id,
                application_id=application_id,
            ),
        )

    async def get_by_admin_id(
        self,
        admin_id: int,
    ) -> AdminProcessingApplicationEntity | None:
        """Получение обрабатываемой админов заявки, если она есть."""
        logger.debug(f"Получение обрабатываемой админом {admin_id=} заявки")
        query = select(self.model).filter_by(admin_id=admin_id)
        res = (await self.session.execute(query)).scalar_one_or_none()
        if not res:
            return None
        return AdminProcessingApplicationEntity(
            data=AdminProcessingApplicationDTO(res.admin_id, res.application_id),
        )

    async def delete(self, admin_id: int) -> None:
        """Удаление связи админа и обрабатываемой им заявки."""
        logger.debug(f"Удаление связи админа {admin_id=} и заявки")
        query = delete(self.model).filter_by(admin_id=admin_id)
        try:
            await self.session.execute(query)
        except Exception as e:
            logger.error(f"Ошибка при удалении связи админа {admin_id=} и заявки: {e}")
