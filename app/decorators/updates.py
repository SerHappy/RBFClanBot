from functools import wraps
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from typing import Callable


def check_application_update(
    return_error_state: int | None = None,
    return_full_user=False,
):
    """Функция декоратор для проверки правильности входящих сообщений при заполнении анкеты."""

    def decorator(update_func: Callable):
        @wraps(update_func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            logger.debug(
                f"Выполняется проверка правильности входящих сообщений при заполнении анкеты для обработчика {update_func.__name__}."
            )
            if update.edited_message:
                logger.warning(
                    f"Получено событие редактирования сообщения при попытке вызова обработчика {update_func.__name__}. Игнорируем его."
                )
                return return_error_state
            user = update.effective_user
            chat = update.effective_chat
            message = update.message
            if user is None or chat is None or message is None:
                # TODO: Добавить уведомление пользователя об ошибке
                logger.critical(
                    f"Получен некорректный user или chat или message при попытке вызова обработчика {update_func.__name__}. Данная ошибка не должна никогда происходить!"
                )
                return ConversationHandler.END
            logger.debug(
                f"Проверка правильности входящих сообщений для обработчика прошла {update_func.__name__} успешно."
            )
            if return_full_user:
                logger.debug(f"Вызываем обработчик {update_func.__name__} с полным user.")
                return await update_func(user=user, chat=chat, message=message, context=context)
            logger.debug(f"Вызываем обработчик {update_func.__name__} с user_id.")
            return await update_func(user_id=user.id, chat=chat, message=message, context=context)

        return wrapper

    return decorator
