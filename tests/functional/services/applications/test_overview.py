import pytest

from app.domain.application.entities import Application
from app.domain.application.exceptions import ApplicationDoesNotExistError
from app.domain.user.entities import User
from app.services.applications.application_overview import ApplicationOverviewService
from tests.environment.unit_of_work import TestUnitOfWork

MAX_ANSWERS = 5


@pytest.fixture()
def service(uow: TestUnitOfWork) -> ApplicationOverviewService:
    return ApplicationOverviewService(uow)


async def test_ok(
    service: ApplicationOverviewService,
    filled_application: Application,
) -> None:
    overview = await service.execute(filled_application.user_id)
    assert overview.count("answer") == MAX_ANSWERS


async def test_doest_not_exists_fail(
    service: ApplicationOverviewService,
    user: User,
) -> None:
    with pytest.raises(ApplicationDoesNotExistError):
        await service.execute(user.id)
