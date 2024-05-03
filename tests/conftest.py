import pytest

from app.domain.application.value_objects import ApplicationStatusEnum
from app.domain.application_answers.entities import ApplicationAnswer
from app.domain.user.dto import UserDTO
from app.domain.user.entities import User
from app.domain.application.entities import Application
from app.domain.application.dto import ApplicationDTO
from app.domain.application_answers.dto import AnswerDTO
from _pytest.fixtures import SubRequest


@pytest.fixture
def user(request: SubRequest) -> User:
    extra_data = getattr(request, "param", {})
    return User(
        data=UserDTO(
            id=1,
            username="@username",
            first_name="name",
            last_name="lastname",
            is_banned=extra_data.get("is_banned", False),
        )
    )


@pytest.fixture
def application(request: SubRequest) -> Application:
    extra_data = getattr(request, "param", {})
    return Application(
        data=ApplicationDTO(
            id=1,
            user_id=1,
            status=extra_data.get("status", ApplicationStatusEnum.IN_PROGRESS),
        ),
        answers=None,
    )


@pytest.fixture
def answer(application: Application) -> ApplicationAnswer:
    return ApplicationAnswer(
        AnswerDTO(
            application_id=application.id,
            question_number=1,
            answer_text="answer",
        )
    )
