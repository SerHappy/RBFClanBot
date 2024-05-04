import pytest

from app.domain.user.entities import User
from app.domain.user.exceptions import UserIsNotBannedError, UserNotFoundError
from app.services.users.user_unban import UserUnbanService
from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
def service(uow: TestUnitOfWork) -> UserUnbanService:
    return UserUnbanService(uow)


async def test_ok(service: UserUnbanService, uow: TestUnitOfWork, user: User) -> None:
    user.ban()
    async with uow():
        created_user = await uow.user.create(user)
        await uow.commit()
    unbanned_user = await service.execute(created_user.id)

    assert unbanned_user.is_banned is False
    assert user.id == unbanned_user.id
    assert user.first_name == unbanned_user.first_name
    assert user.last_name == unbanned_user.last_name
    assert user.username == unbanned_user.username
    assert user.is_banned != unbanned_user.is_banned


async def test_user_not_found_fail(
    service: UserUnbanService,
    uow: TestUnitOfWork,
    user: User,
) -> None:
    with pytest.raises(UserNotFoundError):
        async with uow():
            await service.execute(user.id)


async def test_user_already_unbanned(
    service: UserUnbanService,
    uow: TestUnitOfWork,
    user: User,
) -> None:
    async with uow():
        created_user = await uow.user.create(user)
        await uow.commit()
    with pytest.raises(UserIsNotBannedError):
        async with uow():
            await service.execute(created_user.id)
