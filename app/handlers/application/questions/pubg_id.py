import keyboards
from config import ApplicationStates
from decorators import updates
from loguru import logger
from services import application
from telegram import Chat, Message
from telegram.ext import ContextTypes
from validators import question_validators


@updates.check_application_update()
async def pubg_id(user_id: int, chat: Chat, message: Message, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.pubgID_state.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Это же состояние, если проверка корректности pubg_id не пройдена, иначе следующее состояние.

    """
    if not question_validators.is_only_numbers(message.text):
        logger.debug(f"Получен некорректный pubg_id={message.text} в чате chat_id={chat.id}.")
        await chat.send_message("Проверьте правильность ввода pubg_id. Pubg_id должен состоять только из цифр.")
        return ApplicationStates.pubgID_state

    return await application.process_application_answer(
        user_id=user_id,
        chat=chat,
        message=message,
        question_number=1,
        next_message="Сколько тебе полных лет?",
        keyboard=keyboards.REMOVE_KEYBOARD,
        next_state=ApplicationStates.age_state,
        context=context,
    )
