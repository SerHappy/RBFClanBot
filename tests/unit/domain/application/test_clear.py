import pytest

from app.domain.application.entities import Application
from app.domain.application.exceptions import ApplicationAlreadyCompleteError
from app.domain.application.value_objects import ApplicationStatusEnum
from app.domain.application_answers.entities import ApplicationAnswer


def test_ok(application: Application, answer: ApplicationAnswer) -> None:
    application.add_new_answer(answer)
    application.clear()
    assert application.answers == {}


@pytest.mark.parametrize(
    "application",
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
def test_clear_invalid_status_fail(application: Application) -> None:
    with pytest.raises(ApplicationAlreadyCompleteError):
        application.clear()
