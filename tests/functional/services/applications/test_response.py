import pytest

from app.domain.application.entities import Application
from app.domain.application.exceptions import ApplicationDoesNotExistError
from app.domain.user.entities import User
from app.services.applications.application_response import ApplicationResponseService
from app.services.applications.dto import (
    ApplicationResponseInputDTO,
)
from app.services.applications.value_objects import ApplicationResponseStatusEnum
from tests.environment.unit_of_work import TestUnitOfWork

MAX_ANSWERS = 5


@pytest.fixture()
def service(uow: TestUnitOfWork) -> ApplicationResponseService:
    return ApplicationResponseService(uow)


@pytest.fixture()
def dto(user: User) -> ApplicationResponseInputDTO:
    return ApplicationResponseInputDTO(
        user_id=user.id,
        answer_text="new answer",
        question_number=1,
    )


async def test_add_ok(
    service: ApplicationResponseService,
    empty_application: Application,
    uow: TestUnitOfWork,
    dto: ApplicationResponseInputDTO,
) -> None:
    overview = await service.execute(dto)
    assert overview.status == ApplicationResponseStatusEnum.NEW
    async with uow():
        user_application = await uow.application.retrieve_last(
            empty_application.user_id,
        )
    assert user_application.answers[dto.question_number].answer_text == dto.answer_text
    assert len(user_application.answers) == 1


async def test_update_ok(
    service: ApplicationResponseService,
    filled_application: Application,
    uow: TestUnitOfWork,
    dto: ApplicationResponseInputDTO,
) -> None:
    overview = await service.execute(dto)
    assert overview.status == ApplicationResponseStatusEnum.UPDATE
    async with uow():
        user_application = await uow.application.retrieve_last(
            filled_application.user_id,
        )
    assert user_application.answers[dto.question_number].answer_text == dto.answer_text
    assert len(user_application.answers) == MAX_ANSWERS


async def test_does_not_exists_fail(
    service: ApplicationResponseService,
    dto: ApplicationResponseInputDTO,
) -> None:
    with pytest.raises(ApplicationDoesNotExistError):
        await service.execute(dto)
