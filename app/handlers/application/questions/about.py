from telegram import Chat, Message
from telegram.ext import ContextTypes

from app.decorators import updates
from app.handlers.application.questions.universal.base import handle_question
from app.handlers.application.questions.universal.dto import QuestionResponseDTO


@updates.check_application_update()
async def about_skip(
    user_id: int,
    chat: Chat,  # noqa: ARG001
    message: Message,  # noqa: ARG001
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """
    Handle about skip.

    Args:
        user_id (int): The user id.
        chat (Chat): The chat.
        message (Message): The message.
        context (ContextTypes.DEFAULT_TYPE): The context.

    Returns:
        int: The next state.
    """
    answer = "Пусто"
    data = QuestionResponseDTO(
        bot=context.bot,
        user_id=user_id,
        message_text=answer,  # type: ignore[reportArgumentType]
        question_number=5,
    )
    return await handle_question(data)


@updates.check_application_update()
async def about(
    user_id: int,
    chat: Chat,  # noqa: ARG001
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """
    Handle about.

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
        question_number=5,
    )
    return await handle_question(data)
