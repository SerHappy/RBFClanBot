from app.domain.application_answers.dto import AnswerDTO
from app.domain.application_answers.entities import ApplicationAnswer


def test_create_ok() -> None:
    answer = ApplicationAnswer(
        data=AnswerDTO(
            application_id=1,
            question_number=1,
            answer_text="test",
        ),
    )
    assert answer.application_id == 1
    assert answer.question_number == 1
    assert answer.answer_text == "test"
