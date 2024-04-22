import keyboards
from config import ApplicationStates
from decorators import updates
from services import application
from telegram import Chat, Message
from telegram.ext import ContextTypes


@updates.check_application_update()
async def game_mode(user_id: int, chat: Chat, message: Message, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.game_modes_state.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Следующее состояние.

    """
    return await application.process_application_answer(
        user_id=user_id,
        chat=chat,
        message=message,
        question_number=3,
        next_message="Сколько времени в день готов уделять игре с соклановцами? (примерно; можно по дням)",
        keyboard=keyboards.REMOVE_KEYBOARD,
        next_state=ApplicationStates.activity_state,
        context=context,
    )
