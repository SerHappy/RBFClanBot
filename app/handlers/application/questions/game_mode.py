from config import ApplicationStates
from decorators import updates
from telegram import Chat, Message
from telegram.ext import ContextTypes

from app.handlers.application.questions.universal.base import handle_question
from app.handlers.application.questions.universal.dto import QuestionResponseDTO


@updates.check_application_update()
async def game_mode(
    user_id: int,
    chat: Chat,  # noqa: ARG001
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Обработка ответа состояния ApplicationStates.game_modes_state."""
    data = QuestionResponseDTO(
        bot=context.bot,
        user_id=user_id,
        message_text=message.text,  # type: ignore[reportArgumentType]
        question_number=3,
        next_question_text=(
            "Сколько времени в день готов уделять игре с соклановцами? "
            "(примерно; можно по дням)"
        ),
        next_state=ApplicationStates.ACTIVITY_STATE,
    )
    return await handle_question(data)
