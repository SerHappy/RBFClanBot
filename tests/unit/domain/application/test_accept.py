import pytest

from app.domain.application.entities import Application
from app.domain.application.exceptions import ChangeApplicationStatusError
from app.domain.application.value_objects import ApplicationStatusEnum


def test_ok(application: Application) -> None:
    application.status = ApplicationStatusEnum.PROCESSING
    application.admin_id = 1
    application.accept("link")
    assert application.status == ApplicationStatusEnum.ACCEPTED
    assert application.invite_link == "link"
    assert application.admin_id is None


@pytest.mark.parametrize(
    "application",
    [
        pytest.param(
            {"status": status},
            marks=pytest.mark.usefixtures("application"),
            id=status.name,
        )
        for status in ApplicationStatusEnum
        if status != ApplicationStatusEnum.PROCESSING
    ],
    indirect=True,
)
def test_invalid_status_fail(application: Application) -> None:
    with pytest.raises(ChangeApplicationStatusError):
        application.accept("link")
