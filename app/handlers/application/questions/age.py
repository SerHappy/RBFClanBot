from loguru import logger
from telegram import Chat, Message
from telegram.ext import ContextTypes

from app.decorators import updates
from app.handlers.application.questions.universal.base import handle_question
from app.handlers.application.questions.universal.dto import QuestionResponseDTO
from app.handlers.config import ApplicationStates
from app.validators import question_validators


@updates.check_application_update()
async def age(
    user_id: int,
    chat: Chat,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Обработка ответа состояния ApplicationStates.old_state."""
    if not question_validators.is_digit_between(start=1, end=100, value=message.text):
        logger.debug(
            f"Получен некорректный age={message.text} в чате chat_id={chat.id}.",
        )
        await chat.send_message(
            (
                "Проверьте правильность ввода возраста."
                "Возраст должен быть целым числом от 1 до 100."
            ),
        )
        return ApplicationStates.AGE_STATE

    data = QuestionResponseDTO(
        bot=context.bot,
        user_id=user_id,
        message_text=message.text,  # type: ignore[reportArgumentType]
        question_number=2,
        next_question_text=(
            "Какие режимы игры предпочитаешь больше всего? (можно несколько)"
        ),
        next_state=ApplicationStates.GAME_MODES_STATE,
    )
    return await handle_question(data)
