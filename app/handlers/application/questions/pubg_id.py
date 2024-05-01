from loguru import logger
from telegram import Chat, Message
from telegram.ext import ContextTypes

from app.decorators import updates
from app.handlers.application.questions.universal.base import handle_question
from app.handlers.application.questions.universal.dto import QuestionResponseDTO
from app.handlers.config import ApplicationStates
from app.validators import question_validators


@updates.check_application_update()
async def pubg_id(
    user_id: int,
    chat: Chat,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """
    Handle pubg id answer.

    Args:
        user_id (int): The user id.
        chat (Chat): The chat.
        message (Message): The message.
        context (ContextTypes.DEFAULT_TYPE): The context.

    Returns:
        int: The next state.
    """
    # TODO: Replace with pydantic validator
    if not question_validators.is_only_numbers(message.text):
        logger.debug(
            f"Получен некорректный pubg_id={message.text} в чате chat_id={chat.id}.",
        )
        await chat.send_message(
            (
                "Проверьте правильность ввода pubg_id."
                " Pubg_id должен состоять только из цифр."
            ),
        )
        return ApplicationStates.PUBG_ID_STATE.value

    data = QuestionResponseDTO(
        bot=context.bot,
        user_id=user_id,
        message_text=message.text,  # type: ignore[reportArgumentType]
        question_number=1,
        next_question_text="Сколько тебе полных лет?",
        next_state=ApplicationStates.AGE_STATE,
    )
    return await handle_question(data)
