from db import UnitOfWork


class UserService:
    async def is_user_banned(self, uow: UnitOfWork, user_id: int) -> bool:
        async with uow:
            user = await uow.user.get(user_id)
            if not user:
                raise ValueError
            return user.is_banned
