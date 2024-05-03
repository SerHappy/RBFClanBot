import pytest
from app.domain.application.entities import Application
from app.domain.application.exceptions import ChangeApplicationStatusError
from app.domain.application.value_objects import ApplicationStatusEnum


def test_ok(application: Application) -> None:
    application.status = ApplicationStatusEnum.WAITING
    admin_id = 1
    application.take(admin_id)
    assert application.admin_id == admin_id
    assert application.status == ApplicationStatusEnum.PROCESSING


@pytest.mark.parametrize(
    "application",
    [
        pytest.param({"status": status}, marks=pytest.mark.usefixtures("application"))
        for status in ApplicationStatusEnum
        if status != ApplicationStatusEnum.WAITING
    ],
    indirect=True,
)
def test_invalid_status_fail(application: Application) -> None:
    with pytest.raises(ChangeApplicationStatusError):
        application.take(1)
