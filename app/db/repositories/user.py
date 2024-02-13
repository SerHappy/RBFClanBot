from .abstract import Repository
from models import Application
from models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class UserRepository(Repository[User]):
    """User repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize User repository."""
        super().__init__(type_model=User, session=session)

    async def create(
        self,
        id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_admin: bool = False,
    ) -> User:
        """Create new user.

        Args:
            username: Username (Optional).
            first_name: First name (Optional).
            last_name: Last name (Optional).
            is_admin: Is admin. Default: False.

        Returns:
            User.
        """
        new_user = await self.session.merge(
            self.type_model(
                id=id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_admin=is_admin,
            )
        )
        return new_user

    async def get_last_application(self, user_id: int) -> Application | None:
        """Get last user application.

        Args:
            user_id: User id.

        Returns:
            Application.
        """
        statement = select(User).where(User.id == user_id).options(selectinload(User.applications))
        res = (await self.session.execute(statement)).scalar()
        return res
