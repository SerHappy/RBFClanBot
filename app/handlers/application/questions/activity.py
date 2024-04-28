import keyboards
from config import ApplicationStates
from decorators import updates
from telegram import Chat, Message
from telegram.ext import ContextTypes

from app.handlers.application.questions.universal.base import handle_question
from app.handlers.application.questions.universal.dto import QuestionResponseDTO


@updates.check_application_update()
async def activity(
    user_id: int,
    chat: Chat,  # noqa: ARG001
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Обработка ответа состояния ApplicationStates.activity_state."""
    data = QuestionResponseDTO(
        bot=context.bot,
        user_id=user_id,
        message_text=message.text,  # type: ignore[reportArgumentType]
        question_number=4,
        next_question_text=(
            "Расскажи о себе, либо пропусти вопрос.\n"
            "Чем больше информации мы о тебе получим, "
            "тем выше вероятность одобрения заявки."
        ),
        next_state=ApplicationStates.ABOUT_STATE,
        reply_markup=keyboards.USER_SKIP_KEYBOARD,
    )
    return await handle_question(data)
