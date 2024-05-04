import pytest
from _pytest.fixtures import SubRequest

from app.domain.application.entities import Application
from app.domain.application.value_objects import ApplicationStatusEnum
from app.domain.application_answers.dto import AnswerDTO
from app.domain.application_answers.entities import ApplicationAnswer
from app.domain.user.entities import User
from tests.environment.unit_of_work import TestUnitOfWork


@pytest.fixture()
async def filled_application(
    uow: TestUnitOfWork, user: User, request: SubRequest,
) -> Application:
    extra_data = getattr(request, "param", {})
    async with uow():
        await uow.user.create(user)
        application = await uow.application.create(user_id=user.id)
        for question_number in range(1, 6):
            answer = ApplicationAnswer(
                AnswerDTO(
                    application_id=application.id,
                    question_number=question_number,
                    answer_text="answer",
                ),
            )
            application.add_new_answer(answer)
            await uow.application_answer.add_answer(answer)
        application.status = extra_data.get("status", ApplicationStatusEnum.IN_PROGRESS)
        await uow.application.update(application)
        await uow.commit()
        return application

@pytest.fixture()
async def empty_application(
    uow: TestUnitOfWork, user: User, request: SubRequest,
) -> Application:
    extra_data = getattr(request, "param", {})
    async with uow():
        await uow.user.create(user)
        application = await uow.application.create(user_id=user.id)
        application.status = extra_data.get("status", ApplicationStatusEnum.IN_PROGRESS)
        await uow.application.update(application)
        await uow.commit()
        return application
