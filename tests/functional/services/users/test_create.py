import pytest

from app.domain.user.entities import User
from app.services.users.dto import UserCreateDTO
from app.services.users.user_create import EnsureUserExistsService
from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
def service(uow: TestUnitOfWork) -> EnsureUserExistsService:
    return EnsureUserExistsService(uow)


@pytest.fixture()
def dto() -> UserCreateDTO:
    return UserCreateDTO(
        id=1,
        first_name="John",
        last_name="Doe",
        username="@johndoe",
    )


async def test_ok(
    service: EnsureUserExistsService,
    dto: UserCreateDTO,
    uow: TestUnitOfWork,
) -> None:
    result = await service.execute(dto)

    async with uow():
        user = await uow.user.retrieve(dto.id)

    assert result.id == user.id
    assert result.first_name == user.first_name
    assert result.last_name == user.last_name
    assert result.username == user.username
    assert result.is_banned == user.is_banned is False


async def test_already_created_ok(
    service: EnsureUserExistsService,
    dto: UserCreateDTO,
    user: User,
    uow: TestUnitOfWork,
) -> None:
    async with uow():
        user = await uow.user.create(user)
        await uow.commit()
    result = await service.execute(dto)
    assert result.id == user.id
    assert result.first_name == user.first_name
    assert result.last_name == user.last_name
    assert result.username == user.username
    assert result.is_banned == user.is_banned is False
