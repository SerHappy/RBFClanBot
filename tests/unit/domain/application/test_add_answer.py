import pytest

from app.domain.application.entities import Application
from app.domain.application.exceptions import ApplicationAnswerAlreadyExistError
from app.domain.application_answers.entities import ApplicationAnswer


def test_ok(application: Application, answer: ApplicationAnswer) -> None:
    application.add_new_answer(answer)
    assert application.answers[answer.question_number] == answer
    assert len(application.answers) == answer.question_number


def test_answer_already_exists_fail(
    application: Application,
    answer: ApplicationAnswer,
) -> None:
    application.add_new_answer(answer)

    with pytest.raises(ApplicationAnswerAlreadyExistError):
        application.add_new_answer(answer)
