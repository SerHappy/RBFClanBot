from decorators import updates
from loguru import logger
from services import application
from telegram import Chat
from telegram import Message
from telegram.ext import ContextTypes


@updates.check_application_update()
async def about_skip(
    user_id: int,
    chat: Chat,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """
    Обработка ответа состояния ApplicationStates.about_state при вводе "Пропустить".

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Следующее состояние. Показ обзора анкеты.
    """
    answer = "Пусто"

    if await application._is_new_answer(user_id, 5) is False and context.user_data["application_completed"] is True:  # type: ignore
        logger.debug(f"Пользователь user={user_id} уже отвечал на вопрос about_skip, обновляем его ответ")
        await application._update_answer(user_id, 5, answer)
    else:
        logger.debug(f"Пользователь user={user_id} еще не отвечал на вопрос about_skip, сохраняем его ответ")
        await application._save_answer(user_id, 5, answer)
    logger.info(f"Показать обзор заявки для chat_id={chat.id}")
    return await application.show_overview(chat)


@updates.check_application_update()
async def about(
    user_id: int,
    chat: Chat,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """
    Обработка ответа состояния ApplicationStates.about_state при вводе текста о себе.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Следующее состояние. Показ обзора анкеты.
    """
    if await application._is_new_answer(user_id, 5) is False and context.user_data["application_completed"] is True:  # type: ignore
        logger.debug(f"Пользователь user={user_id} уже отвечал на вопрос about, обновляем его ответ")
        await application._update_answer(user_id, 5, message.text)
    else:
        logger.debug(f"Пользователь user={user_id} еще не отвечал на вопрос about, сохраняем его ответ")
        await application._save_answer(user_id, 5, message.text)
    logger.info(f"Показать обзор заявки для chat_id={chat.id}")
    return await application.show_overview(chat)
