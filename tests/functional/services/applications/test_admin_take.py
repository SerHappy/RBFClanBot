import pytest

from app.domain.admin_processing_application.dto import AdminProcessingApplicationDTO
from app.domain.admin_processing_application.entities import AdminProcessingApplication
from app.domain.admin_processing_application.exceptions import (
    AdminAlreadyProcessedApplicationError,
)
from app.domain.application.entities import Application
from app.domain.application.exceptions import (
    ApplicationDoesNotExistError,
    ChangeApplicationStatusError,
)
from app.domain.application.value_objects import ApplicationStatusEnum
from app.domain.user.entities import User
from app.services.applications.application_admin_take import ApplicationAdminTakeService
from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
def service(uow: TestUnitOfWork) -> ApplicationAdminTakeService:
    return ApplicationAdminTakeService(uow)


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
    service: ApplicationAdminTakeService,
    filled_application: Application,
    uow: TestUnitOfWork,
) -> None:
    filled_application.complete()
    async with uow():
        await uow.application.update(filled_application)
        await uow.commit()
    await service.execute(
        admin_id=filled_application.user_id, application_id=filled_application.id,
    )


async def test_does_not_exists_fail(
    service: ApplicationAdminTakeService,
    user: User,
) -> None:
    with pytest.raises(ApplicationDoesNotExistError):
        await service.execute(admin_id=user.id, application_id=10)


@pytest.mark.parametrize(
    "filled_application",
    [
        pytest.param(
            {"status": status},
            marks=pytest.mark.usefixtures("filled_application"),
            id=status.name,
        )
        for status in ApplicationStatusEnum
        if status != ApplicationStatusEnum.WAITING
    ],
    indirect=True,
)
async def test_wrong_status_fail(
    service: ApplicationAdminTakeService,
    filled_application: Application,
) -> None:
    with pytest.raises(ChangeApplicationStatusError):
        await service.execute(
            admin_id=filled_application.user_id,
            application_id=filled_application.id,
        )


async def test_admin_already_processing_fail(
    service: ApplicationAdminTakeService,
    admin_application: AdminProcessingApplication,
) -> None:
    with pytest.raises(AdminAlreadyProcessedApplicationError):
        await service.execute(
            admin_id=admin_application.admin_id,
            application_id=admin_application.application_id,
        )
