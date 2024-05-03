import pytest
from app.domain.application.entities import Application
from app.domain.application.exceptions import ApplicationAnswerDoesNotExistError
from app.domain.application.value_objects import ApplicationStatusEnum
from app.domain.application_answers.entities import ApplicationAnswer
from app.domain.application_answers.dto import AnswerDTO


def test_ok(application: Application, answer: ApplicationAnswer) -> None:
    application.add_new_answer(answer)
    assert application.answers[answer.question_number] == answer
    new_answer = ApplicationAnswer(
        AnswerDTO(
            application_id=application.id,
            question_number=answer.question_number,
            answer_text="new answer",
        )
    )
    application.update_answer(new_answer)
    assert application.answers[new_answer.question_number] == new_answer
    assert len(application.answers) == 1


def test_answer_does_not_exists_fail(
    application: Application,
    answer: ApplicationAnswer,
) -> None:
    with pytest.raises(ApplicationAnswerDoesNotExistError):
        application.update_answer(answer)
