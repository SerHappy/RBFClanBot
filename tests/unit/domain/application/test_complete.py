import pytest
from app.domain.application.entities import Application
from app.domain.application.exceptions import (
    ApplicationDoesNotCompeteError,
    ChangeApplicationStatusError,
)
from app.domain.application.value_objects import ApplicationStatusEnum
from app.domain.application_answers.entities import ApplicationAnswer
from app.domain.application_answers.dto import AnswerDTO


def test_ok(application: Application) -> None:
    for question_number in range(1, 6):
        answer = ApplicationAnswer(
            AnswerDTO(
                application_id=application.id,
                question_number=question_number,
                answer_text="answer",
            )
        )
        application.add_new_answer(answer)
    application.complete()


@pytest.mark.parametrize(
    "application",
    [
        pytest.param({"status": status}, marks=pytest.mark.usefixtures("application"))
        for status in ApplicationStatusEnum
        if status != ApplicationStatusEnum.IN_PROGRESS
    ],
    indirect=True,
)
def test_invalid_status_fail(application: Application) -> None:
    for question_number in range(1, 6):
        answer = ApplicationAnswer(
            AnswerDTO(
                application_id=application.id,
                question_number=question_number,
                answer_text="answer",
            )
        )
        application.add_new_answer(answer)
    with pytest.raises(ChangeApplicationStatusError):
        application.complete()


def test_does_not_complete_fail(application: Application) -> None:
    with pytest.raises(ApplicationDoesNotCompeteError):
        application.complete()
