from app.services.users.user_create import EnsureUserExistsService
from app.services.users.dto import UserCreateDTO
from tests.environment.unit_of_work import TestUnitOfWork
import pytest
from _pytest.fixtures import SubRequest
from app.domain.user.entities import User


@pytest.fixture
def service(uow: TestUnitOfWork) -> EnsureUserExistsService:
    return EnsureUserExistsService(uow)


@pytest.fixture
def dto(request: SubRequest) -> UserCreateDTO:
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
    assert result.is_banned == user.is_banned == False


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
    assert result.is_banned == user.is_banned == False
