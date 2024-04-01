from config import ApplicationStates
from decorators import updates
from services import application
from telegram import Chat
from telegram import Message
from telegram.ext import ContextTypes

import keyboards


@updates.check_application_update()
async def activity(user_id: int, chat: Chat, message: Message, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.activity_state.

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
        question_number=4,
        next_message="Расскажи о себе, либо пропусти вопрос.\n"
        + "Чем больше информации мы о тебе получим, тем выше вероятность одобрения заявки.",
        keyboard=keyboards.USER_SKIP_KEYBOARD,
        next_state=ApplicationStates.about_state,
        context=context,
    )
