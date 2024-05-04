import pytest

from app.domain.application.entities import Application
from app.domain.application.exceptions import ApplicationDoesNotExistError
from app.services.applications.application_formatting import (
    ApplicationFormattingService,
)
from tests.environment.unit_of_work import TestUnitOfWork

MAX_ANSWERS = 5

@pytest.fixture()
def service(uow: TestUnitOfWork) -> ApplicationFormattingService:
    return ApplicationFormattingService(uow)


async def test_ok(
    service: ApplicationFormattingService,
    filled_application: Application,
) -> None:
    formatted_application = await service.execute(filled_application.id)
    assert formatted_application.startswith(f"ЗАЯВКА №{filled_application.id}")
    assert formatted_application.count("answer") == MAX_ANSWERS


async def test_doest_not_exists_fail(
    service: ApplicationFormattingService,
) -> None:
    with pytest.raises(ApplicationDoesNotExistError):
        await service.execute(1)
