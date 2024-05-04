import pytest

from app.domain.admin_processing_application.dto import AdminProcessingApplicationDTO
from app.domain.admin_processing_application.entities import AdminProcessingApplication
from app.domain.admin_processing_application.exceptions import (
    ApplicationAlreadyProcessedError,
    WrongAdminError,
)
from app.domain.application.entities import Application
from app.domain.application.exceptions import (
    ChangeApplicationStatusError,
)
from app.domain.application.value_objects import ApplicationStatusEnum
from app.services.applications.application_admin_reject import (
    ApplicationAdminRejectService,
)
from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
def service(uow: TestUnitOfWork) -> ApplicationAdminRejectService:
    return ApplicationAdminRejectService(uow)


@pytest.fixture()
async def admin_application(
    filled_application: Application,
    uow: TestUnitOfWork,
) -> AdminProcessingApplication:
    filled_application.complete()
    filled_application.take(admin_id=filled_application.user_id)
    async with uow():
        entity = AdminProcessingApplication(
            data=AdminProcessingApplicationDTO(
                admin_id=filled_application.user_id,
                application_id=filled_application.id,
            ),
        )
        await uow.admin_processing_application.create(entity)
        await uow.application.update(filled_application)
        await uow.commit()
    return entity


async def test_ok(
    service: ApplicationAdminRejectService,
    admin_application: AdminProcessingApplication,
) -> None:
    accepted_application = await service.execute(
        admin_application.admin_id,
        admin_application.application_id,
        "reason",
    )
    assert accepted_application.status == ApplicationStatusEnum.REJECTED
    assert accepted_application.rejection_reason == "reason"
    assert accepted_application.admin_id is None


async def test_already_processed_fail(
    service: ApplicationAdminRejectService,
    admin_application: AdminProcessingApplication,
) -> None:
    with pytest.raises(ApplicationAlreadyProcessedError):
        await service.execute(
            -1,
            admin_application.application_id,
            "reject",
        )


async def test_wrong_admin_fail(
    service: ApplicationAdminRejectService,
    admin_application: AdminProcessingApplication,
) -> None:
    with pytest.raises(WrongAdminError):
        await service.execute(
            admin_application.admin_id,
            -1,
            "reject",
        )


@pytest.mark.parametrize(
    "status",
    [
        status
        for status in ApplicationStatusEnum
        if status != ApplicationStatusEnum.PROCESSING
    ],
    ids=[
        status.name
        for status in ApplicationStatusEnum
        if status != ApplicationStatusEnum.PROCESSING
    ],
)
async def test_wrong_status_fail(
    service: ApplicationAdminRejectService,
    admin_application: AdminProcessingApplication,
    status: ApplicationStatusEnum,
    uow: TestUnitOfWork,
) -> None:
    async with uow():
        application = await uow.application.get_by_id(admin_application.application_id)
        application.status = status
        await uow.application.update(application)
        await uow.commit()
    with pytest.raises(ChangeApplicationStatusError):
        await service.execute(
            admin_application.admin_id,
            admin_application.application_id,
            "reject",
        )
