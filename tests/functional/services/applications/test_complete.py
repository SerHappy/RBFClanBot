import pytest

from app.domain.application.entities import Application
from app.domain.application.exceptions import (
    ApplicationDoesNotCompeteError,
    ApplicationDoesNotExistError,
    ChangeApplicationStatusError,
)
from app.domain.application.value_objects import ApplicationStatusEnum
from app.domain.user.entities import User
from app.services.applications.application_complete import ApplicationCompleteService
from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
def service(uow: TestUnitOfWork) -> ApplicationCompleteService:
    return ApplicationCompleteService(uow)


async def test_add_ok(
    service: ApplicationCompleteService,
    filled_application: Application,
) -> None:
    completed_application = await service.execute(filled_application.user_id)
    assert completed_application.status == ApplicationStatusEnum.WAITING


async def test_does_not_exists_fail(
    service: ApplicationCompleteService,
    user: User,
) -> None:
    with pytest.raises(ApplicationDoesNotExistError):
        await service.execute(user.id)


async def test_does_not_complete_fail(
    service: ApplicationCompleteService,
    empty_application: Application,
) -> None:
    with pytest.raises(ApplicationDoesNotCompeteError):
        await service.execute(empty_application.user_id)


@pytest.mark.parametrize(
    "filled_application",
    [
        pytest.param(
            {"status": status},
            marks=pytest.mark.usefixtures("application"),
            id=status.name,
        )
        for status in ApplicationStatusEnum
        if status != ApplicationStatusEnum.IN_PROGRESS
    ],
    indirect=True,
)
async def test_wrong_status_fail(
    service: ApplicationCompleteService,
    filled_application: Application,
) -> None:
    with pytest.raises(ChangeApplicationStatusError):
        await service.execute(filled_application.user_id)
