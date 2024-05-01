from telegram import Chat, Message
from telegram.ext import ContextTypes

from app.decorators import updates
from app.handlers.application.questions.universal.base import handle_question
from app.handlers.application.questions.universal.dto import QuestionResponseDTO
from app.handlers.config import ApplicationStates


@updates.check_application_update()
async def game_mode(
    user_id: int,
    chat: Chat,  # noqa: ARG001
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """
    Handle game mode answer.

    Args:
        user_id (int): The user id.
        chat (Chat): The chat.
        message (Message): The message.
        context (ContextTypes.DEFAULT_TYPE): The context.

    Returns:
        int: The next state.
    """
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
