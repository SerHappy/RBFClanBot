from loguru import logger
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.abstract import Repository
from app.domain.admin_processing_application.dto import AdminProcessingApplicationDTO
from app.domain.admin_processing_application.entities import (
    AdminProcessingApplication as AdminProcessingApplicationEntity,
)
from app.domain.admin_processing_application.exceptions import (
    ApplicationAlreadyProcessedError,
)
from app.models import AdminProcessingApplication


class AdminProcessingApplicationRepository(Repository[AdminProcessingApplication]):
    """Репозиторий для работы с связями админов и обрабатываемых ими заявок."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=AdminProcessingApplication, session=session)

    async def create(
        self,
        entity: AdminProcessingApplicationEntity,
    ) -> AdminProcessingApplicationEntity:
        """Создание связи админа и обрабатываемой им заявки."""
        query = insert(self.model).values(
            admin_id=entity.admin_id,
            application_id=entity.application_id,
        )
        try:
            await self.session.execute(query)
        except IntegrityError as e:
            raise ApplicationAlreadyProcessedError from e
        return entity

    async def get_by_admin_id(
        self,
        admin_id: int,
    ) -> AdminProcessingApplicationEntity | None:
        """Получение обрабатываемой админов заявки, если она есть."""
        logger.debug(f"Получение обрабатываемой админом {admin_id=} заявки")
        query = select(self.model).filter_by(admin_id=admin_id)
        res = (await self.session.execute(query)).scalar_one_or_none()
        # TODO: Raise does not exist
        if not res:
            return None
        return self._get_entity(res)

    async def delete(self, entity: AdminProcessingApplicationEntity) -> None:
        """Удаление связи админа и обрабатываемой им заявки."""
        query = delete(self.model).filter_by(
            admin_id=entity.admin_id,
            application_id=entity.application_id,
        )
        await self.session.execute(query)

    def _get_entity(
        self,
        obj: AdminProcessingApplication,
    ) -> AdminProcessingApplicationEntity:
        return AdminProcessingApplicationEntity(
            data=AdminProcessingApplicationDTO(
                admin_id=obj.admin_id,
                application_id=obj.application_id,
            ),
        )
