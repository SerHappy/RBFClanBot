from app import keyboards
from app.db.engine import UnitOfWork
from app.handlers.application.questions.universal.dto import QuestionResponseDTO
from app.handlers.config.states import ApplicationStates
from app.services.applications.application_overview import ApplicationOverviewService
from app.services.applications.application_response import ApplicationResponseService
from app.services.applications.dto import (
    ApplicationResponseInputDTO,
    ApplicationResponseStatusEnum,
)


# TODO: Refactor this and DTO for more simplification
async def handle_question(data: QuestionResponseDTO) -> int:
    """Universal question handler."""
    uow = UnitOfWork()
    application_response_service = ApplicationResponseService(uow)
    response_data = ApplicationResponseInputDTO(
        user_id=data.user_id,
        answer_text=data.message_text,
        question_number=data.question_number,
    )
    output_status = await application_response_service.execute(data=response_data)
    if (
        data.next_question_text
        and data.next_state
        and output_status.status == ApplicationResponseStatusEnum.NEW
    ):
        await data.bot.send_message(
            chat_id=data.user_id,
            text=data.next_question_text,
            reply_markup=data.reply_markup,
        )
        return data.next_state.value
    overview_service = ApplicationOverviewService(uow)
    overview_text = await overview_service.execute(data.user_id)
    await data.bot.send_message(
        chat_id=data.user_id,
        text=overview_text,
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )
    await data.bot.send_message(
        chat_id=data.user_id,
        text=(
            "1) Изменить PubgID\n"
            "2) Изменить возраст\n"
            "3) Изменить режимы игры\n"
            "4) Изменить частоту активности\n"
            "5) Изменить 'о себе'\n"
            "6) Все верно!"
        ),
        reply_markup=keyboards.USER_DECISION_KEYBOARD,
    )
    return ApplicationStates.CHANGE_OR_ACCEPT_STATE.value
