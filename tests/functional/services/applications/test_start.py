from datetime import datetime, timedelta, timezone

import pytest

from app.domain.application.entities import Application
from app.domain.application.exceptions import (
    ApplicationAlreadyAcceptedError,
    ApplicationAtWaitingStatusError,
    ApplicationCoolDownError,
)
from app.domain.application.value_objects import ApplicationStatusEnum
from app.domain.user.entities import User
from app.domain.user.exceptions import UserNotFoundError
from app.services.applications.application_start import ApplicationStartService
from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
def service(uow: TestUnitOfWork) -> ApplicationStartService:
    return ApplicationStartService(uow)


async def test_ok(
    service: ApplicationStartService,
    uow: TestUnitOfWork,
    user: User,
) -> None:
    async with uow():
        created_user = await uow.user.create(user)
        await uow.commit()
    application_service = await service.execute(created_user.id)

    async with uow:
        application_repo = await uow.application.get_by_id(application_service.id)

    assert application_service.id == application_repo.id
    assert application_service.user_id == application_repo.user_id
    assert application_service.status == application_repo.status
    assert application_service.answers == application_repo.answers == {}
    assert application_service.invite_link == application_repo.invite_link is None
    assert application_service.decision_date == application_repo.decision_date is None
    assert application_service.admin_id == application_repo.admin_id is None
    assert (
        application_service.rejection_reason
        == application_repo.rejection_reason
        is None
    )


async def test_user_not_found_fail(
    service: ApplicationStartService,
    uow: TestUnitOfWork,
    user: User,
) -> None:
    with pytest.raises(UserNotFoundError):
        async with uow:
            await service.execute(user.id)


@pytest.mark.parametrize(
    "filled_application",
    [
        pytest.param(
            {"status": status},
            marks=pytest.mark.usefixtures("filled_application"),
            id=status.name,
        )
        for status in ApplicationStatusEnum
        if status in [ApplicationStatusEnum.WAITING, ApplicationStatusEnum.PROCESSING]
    ],
    indirect=True,
)
async def test_waiting_status_fail(
    service: ApplicationStartService,
    filled_application: Application,
) -> None:
    with pytest.raises(ApplicationAtWaitingStatusError):
        await service.execute(filled_application.user_id)


@pytest.mark.parametrize(
    "filled_application",
    [
        pytest.param(
            {"status": status},
            marks=pytest.mark.usefixtures("filled_application"),
            id=status.name,
        )
        for status in ApplicationStatusEnum
        if status in [ApplicationStatusEnum.ACCEPTED]
    ],
    indirect=True,
)
async def test_already_accepted_fail(
    service: ApplicationStartService,
    filled_application: Application,
) -> None:
    with pytest.raises(ApplicationAlreadyAcceptedError):
        await service.execute(filled_application.user_id)


@pytest.mark.parametrize(
    "filled_application",
    [
        pytest.param(
            {"status": status},
            marks=pytest.mark.usefixtures("filled_application"),
            id=status.name,
        )
        for status in ApplicationStatusEnum
        if status in [ApplicationStatusEnum.PROCESSING]
    ],
    indirect=True,
)
async def test_cooldown_fail(
    service: ApplicationStartService,
    uow: TestUnitOfWork,
    filled_application: Application,
) -> None:
    async with uow():
        filled_application.reject("reason")
        await uow.application.update(filled_application)
        await uow.commit()
    with pytest.raises(ApplicationCoolDownError):
        await service.execute(filled_application.user_id)


@pytest.mark.parametrize(
    "filled_application",
    [
        pytest.param(
            {"status": status},
            marks=pytest.mark.usefixtures("filled_application"),
            id=status.name,
        )
        for status in ApplicationStatusEnum
        if status in [ApplicationStatusEnum.PROCESSING]
    ],
    indirect=True,
)
async def test_rejected_ok(
    service: ApplicationStartService,
    uow: TestUnitOfWork,
    filled_application: Application,
) -> None:
    async with uow():
        filled_application.reject("reason")
        filled_application.decision_date = datetime.now(tz=timezone.utc) - timedelta(
            days=30,
        )
        await uow.application.update(filled_application)
        await uow.commit()
    await service.execute(filled_application.user_id)
