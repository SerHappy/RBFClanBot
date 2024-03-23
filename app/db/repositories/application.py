from .abstract import Repository
from datetime import datetime
from loguru import logger
from models import Application
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


class ApplicationRepository(Repository[Application]):
    """Application repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize Application repository."""
        super().__init__(type_model=Application, session=session)

    async def create(
        self,
        user_id: int,
        status_id: int | None = 1,
        submission_at: str | None = None,
        decision_date: str | None = None,
        rejection_reason: str | None = None,
        invite_link: str | None = None,
    ) -> Application:
        """
        Create new application.

        Args:
            user_id: User id.
            status_id: Status id. Default: 1
            submission_at: Submission at (Optional).
            decision_date: Decision date (Optional).
            rejection_reason: Rejection reason (Optional).
            invite_link: Invite link (Optional).

        Returns:
            Application.
        """
        logger.debug(f"Creating new application for user_id={user_id}")
        await self.session.merge(
            self.type_model(
                user_id=user_id,
                status_id=status_id,
                submission_at=submission_at,
                decision_date=decision_date,
                rejection_reason=rejection_reason,
                invite_link=invite_link,
            )
        )

    # TODO: Change to get active application, because it's more clear
    async def _get_last_application(self, user_id: int) -> Application | None:
        """Get last user application.

        Args:
            user_id: User id.

        Returns:
            Application or None.
        """
        logger.debug(f"Getting last application for user_id={user_id}")
        statement = (
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.decision_date.desc())
            .limit(1)
        )
        res = (await self.session.execute(statement)).scalar()
        return res

    async def create_if_not_exists(self, user_id: int) -> Application:
        """
        Получить или создать заявку пользователя с заданным user_id.

        Args:
            user_id: ID пользователя.

        Returns:
            Заявка пользователя Application.
        """
        application = await self._get_last_application(user_id)
        if application is None:
            await self.create(user_id)
            application = await self._get_last_application(user_id)
        return application

    async def change_status(self, application_id: int, status_id: int) -> None:
        """Change application status."""
        logger.debug(f"Changing application status for application_id={application_id} to status_id={status_id}")
        statement = update(Application).where(Application.id == application_id).values(status_id=status_id)
        await self.session.execute(statement)

    async def approve_application(self, application_id: int, invite_link: str) -> None:
        """Approve application."""
        logger.debug(f"Approving application for application_id={application_id}")
        await self.change_status(application_id, 3)
        statement = (
            update(Application)
            .where(Application.id == application_id)
            .values(decision_date=datetime.now(), invite_link=invite_link)
        )
        await self.session.execute(statement)

    async def reject_application(self, application_id: int, rejection_reason: str) -> None:
        """Reject application."""
        logger.debug(f"Rejecting application for application_id={application_id}")
        await self.change_status(application_id, 4)
        statement = (
            update(Application)
            .where(Application.id == application_id)
            .values(decision_date=datetime.now(), rejection_reason=rejection_reason)
        )
        await self.session.execute(statement)
