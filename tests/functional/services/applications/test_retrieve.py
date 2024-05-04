import pytest

from app.domain.application.entities import Application
from app.domain.application.exceptions import ApplicationDoesNotExistError
from app.domain.user.entities import User
from app.services.applications.application_retrieve import ApplicationRetrieveService
from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
def service(uow: TestUnitOfWork) -> ApplicationRetrieveService:
    return ApplicationRetrieveService(uow)


async def test_ok(
    service: ApplicationRetrieveService,
    filled_application: Application,
) -> None:
    application = await service.execute(filled_application.user_id)
    assert application.id == filled_application.id
    assert application.user_id == filled_application.user_id
    assert len(application.answers) == len(filled_application.answers)
    assert application.status == filled_application.status
    assert application.admin_id == filled_application.admin_id


async def test_doest_not_exists_fail(
    service: ApplicationRetrieveService,
    user: User,
) -> None:
    with pytest.raises(ApplicationDoesNotExistError):
        await service.execute(user.id)
