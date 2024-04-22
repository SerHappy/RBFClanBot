import keyboards
from config import ApplicationStates
from decorators import updates
from loguru import logger
from services import application
from telegram import Chat, Message
from telegram.ext import ContextTypes
from validators import question_validators


@updates.check_application_update()
async def age(user_id: int, chat: Chat, message: Message, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.old_state.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Это же состояние, если проверка корректности возраста не пройдена, иначе следующее состояние.

    """
    if not question_validators.is_digit_between(start=1, end=100, value=message.text):
        logger.debug(f"Получен некорректный age={message.text} в чате chat_id={chat.id}.")
        await chat.send_message("Проверьте правильность ввода возраста. Возраст должен быть целым числом от 1 до 100.")
        return ApplicationStates.age_state

    return await application.process_application_answer(
        user_id=user_id,
        chat=chat,
        message=message,
        question_number=2,
        next_message="Какие режимы игры предпочитаешь больше всего? (можно несколько)",
        keyboard=keyboards.REMOVE_KEYBOARD,
        next_state=ApplicationStates.game_modes_state,
        context=context,
    )
