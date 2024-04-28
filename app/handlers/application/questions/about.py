from decorators import updates
from telegram import Chat, Message
from telegram.ext import ContextTypes

from app.handlers.application.questions.universal.base import handle_question
from app.handlers.application.questions.universal.dto import QuestionResponseDTO


@updates.check_application_update()
async def about_skip(
    user_id: int,
    chat: Chat,  # noqa: ARG001
    message: Message,  # noqa: ARG001
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Обработка ответа состояния при вводе "Пропустить"."""
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
    """Обработка ответа состояния при вводе текста о себе."""
    data = QuestionResponseDTO(
        bot=context.bot,
        user_id=user_id,
        message_text=message.text,  # type: ignore[reportArgumentType]
        question_number=5,
    )
    return await handle_question(data)
