from datetime import datetime

from loguru import logger
from models import Application
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .abstract import Repository


class ApplicationRepository(Repository[Application]):
    """Репозиторий для работы с заявками."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        super().__init__(type_model=Application, session=session)

    async def create(
        self,
        user_id: int,
        status_id: int | None = 1,
        decision_date: str | None = None,
        rejection_reason: str | None = None,
        invite_link: str | None = None,
    ) -> Application:
        """
        Создание заявки.

        Args:
            user_id: Идентификатор пользователя.
            status_id: Идентификатор статуса заявки. По умолчанию равен 1.
            decision_date: Дата решения (Optional).
            rejection_reason: Причина отклонения (Optional).
            invite_link: Ссылка на приглашение (Optional).

        Returns:
            Экземпляр Application (созданный).
        """
        logger.debug(f"Создание заявки для пользователя с id={user_id}")
        application = await self.session.merge(
            self.type_model(
                user_id=user_id,
                status_id=status_id,
                decision_date=decision_date,
                rejection_reason=rejection_reason,
                invite_link=invite_link,
            )
        )
        logger.debug(f"Создана заявка для пользователя с id={user_id}")
        return application

    async def get_active_application(self, user_id: int) -> Application | None:
        """Получить активную заявку пользователя.

        Args:
            user_id: ID пользователя.

        Returns:
            Заявка пользователя Application или None.
        """
        logger.debug(f"Получение активной заявки пользователя с id={user_id}")
        statement = (
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.decision_date.desc())
            .limit(1)
        )
        res = (await self.session.execute(statement)).scalar()
        if res is None:
            logger.debug(f"Не найдена активная заявка пользователя с id={user_id}")
            return None
        logger.debug(f"Найдена активная заявка пользователя с id={user_id}")
        return res

    async def create_if_not_exists(self, user_id: int) -> Application:
        """
        Создание заявки в случае ее отсутствия.

        Args:
            user_id: ID пользователя.

        Returns:
            Заявка пользователя Application.
        """
        logger.debug(f"Создание или получение активной заявки пользователя с id={user_id}")
        application = await self.get_active_application(user_id)
        if application is None:
            logger.debug(f"Заявка пользователя с id={user_id} не существует, создаем")
            application = await self.create(user_id)
        return application

    async def change_status(self, application_id: int, status_id: int) -> None:
        """
        Смена статуса заявки.

        Args:
            application_id: ID заявки.
            status_id: ID статуса.

        Returns:
            None
        """
        logger.debug(f"Смена статуса заявки application_id={application_id} на status_id={status_id}")
        statement = update(Application).where(Application.id == application_id).values(status_id=status_id)
        await self.session.execute(statement)
        logger.debug(f"Статус заявки application_id={application_id} изменен на status_id={status_id}")

    async def approve_application(self, application_id: int, invite_link: str) -> None:
        """
        Принятие заявки.

        Перевод статуса заявки в 3 и добавление ссылки на приглашение.

        Args:
            application_id: ID заявки.
            invite_link: Ссылка на приглашение.

        Returns:
            None
        """
        logger.debug(
            f"Принятие заявки application_id={application_id}, перевод в статус 3 и добавление ссылки invite_link={invite_link}"
        )
        await self.change_status(application_id, 3)
        statement = (
            update(Application)
            .where(Application.id == application_id)
            .values(decision_date=datetime.now(), invite_link=invite_link)
        )
        await self.session.execute(statement)
        logger.debug(f"Заявка application_id={application_id} принята")

    async def reject_application(self, application_id: int, rejection_reason: str) -> None:
        """
        Отклонение заявки.

        Перевод статуса заявки в 4 и добавление причины отклонения.

        Args:
            application_id: ID заявки.
            rejection_reason: Причина отклонения.

        Returns:
            None
        """
        logger.debug(
            f"Отклонение заявки application_id={application_id}, перевод в статус 4 и добавление причины rejection_reason={rejection_reason}"
        )
        await self.change_status(application_id, 4)
        statement = (
            update(Application)
            .where(Application.id == application_id)
            .values(decision_date=datetime.now(), rejection_reason=rejection_reason)
        )
        await self.session.execute(statement)
        logger.debug(f"Заявка application_id={application_id} отклонена")
