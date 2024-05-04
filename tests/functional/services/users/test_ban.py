import pytest

from app.domain.user.entities import User
from app.domain.user.exceptions import UserIsBannedError, UserNotFoundError
from app.services.users.user_ban import UserBanService
from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
def service(uow: TestUnitOfWork) -> UserBanService:
    return UserBanService(uow)


async def test_ok(service: UserBanService, uow: TestUnitOfWork, user: User) -> None:
    async with uow():
        created_user = await uow.user.create(user)
        await uow.commit()
    banned_user = await service.execute(created_user.id)

    assert banned_user.is_banned is True
    assert user.id == banned_user.id
    assert user.first_name == banned_user.first_name
    assert user.last_name == banned_user.last_name
    assert user.username == banned_user.username
    assert user.is_banned != banned_user.is_banned


async def test_user_not_found_fail(
    service: UserBanService,
    uow: TestUnitOfWork,
    user: User,
) -> None:
    with pytest.raises(UserNotFoundError):
        async with uow():
            await service.execute(user.id)


async def test_user_already_banned(
    service: UserBanService,
    uow: TestUnitOfWork,
    user: User,
) -> None:
    async with uow():
        created_user = await uow.user.create(user)
        created_user.ban()
        await uow.user.update(created_user)
        await uow.commit()
    with pytest.raises(UserIsBannedError):
        async with uow():
            await service.execute(created_user.id)
